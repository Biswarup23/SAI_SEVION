import sys
import threading
import time
import logging
import ctypes
from ctypes import wintypes
import pyperclip

from sai_devion.utils.clipboard import reliable_copy, reliable_paste
from sai_devion.utils.notifications import show_notification
from sai_devion.config import APP_NAME, MAX_WORDS, POLISH_URL
from sai_devion.api_client import api
from sai_devion.session_store import SessionStore


# ==============================
# WinAPI / Hotkey (Windows only)
# ==============================
if sys.platform == "win32":
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # WinAPI constants
    WM_HOTKEY = 0x0312
    WM_QUIT = 0x0012

    MOD_CONTROL = 0x0002  # Ctrl
    # If you ever want Ctrl+Shift etc:
    # MOD_SHIFT   = 0x0004
    # MOD_ALT     = 0x0001
    # MOD_WIN     = 0x0008

    HOTKEY_ID_PROGRAM = 1  # Ctrl + Q
    HOTKEY_ID_QUERY = 2    # Ctrl + W

    VK_Q = 0x51  # virtual key code for 'Q'
    VK_W = 0x57  # virtual key code for 'W'

    class POINT(ctypes.Structure):
        _fields_ = [
            ("x", wintypes.LONG),
            ("y", wintypes.LONG),
        ]

    class MSG(ctypes.Structure):
        _fields_ = [
            ("hwnd",   wintypes.HWND),
            ("message", wintypes.UINT),
            ("wParam", wintypes.WPARAM),
            ("lParam", wintypes.LPARAM),
            ("time",   wintypes.DWORD),
            ("pt",     POINT),
        ]
else:
    user32 = None
    kernel32 = None


class HotkeyHandler:
    def __init__(self, store: SessionStore, get_modes_callable):
        """
        get_modes_callable should return (mode_q, mode_w)
        where mode_q is dict for PROGRAM, mode_w for QUERY
        """
        self.store = store
        self.get_modes = get_modes_callable

        # WinAPI hotkey thread + id (Windows only)
        self._hotkey_thread = None
        self._hotkey_thread_id = None

    # ==============================
    # Public API
    # ==============================
    def register_hotkeys(self):
        """
        Register global hotkeys using WinAPI RegisterHotKey:
          - Ctrl + Q → PROGRAM
          - Ctrl + W → QUERY
        Runs a background message loop thread.
        """
        if sys.platform != "win32":
            show_notification(APP_NAME, "Global hotkeys via WinAPI work only on Windows.")
            logging.warning("Hotkey registration skipped: not on Windows")
            return

        try:
            # Stop previous thread if already running
            self._stop_hotkey_thread()

            # Start a new hotkey listener thread
            self._hotkey_thread = threading.Thread(
                target=self._hotkey_loop,
                daemon=True,
                name="SAI_Devion_HotkeyThread",
            )
            self._hotkey_thread.start()

            # Show current modes in notification
            mode_q, mode_w = self.get_modes()
            show_notification(
                APP_NAME,
                (
                    "Hotkeys enabled (WinAPI):\n"
                    "Ctrl+Q → PROGRAM ({})\n"
                    "Ctrl+W → QUERY ({})"
                ).format(mode_q["lang"], mode_w["lang"])
            )

        except Exception as e:
            logging.exception("Hotkey registration failed")
            show_notification(
                APP_NAME,
                f"Hotkey registration failed. Try running as Admin if needed.\n{e}"
            )

    # Call this if you ever want to cleanly stop the listener (e.g. on app shutdown)
    def stop(self):
        self._stop_hotkey_thread()

    # ==============================
    # Internal: WinAPI hotkey loop
    # ==============================
    def _hotkey_loop(self):
        """
        Runs in background thread:
        - Registers Ctrl+Q and Ctrl+W
        - Listens for WM_HOTKEY and dispatches to _process()
        """
        try:
            # Remember this thread id so we can PostThreadMessage WM_QUIT
            self._hotkey_thread_id = kernel32.GetCurrentThreadId()

            # Register Ctrl + Q → PROGRAM
            if not user32.RegisterHotKey(
                None,
                HOTKEY_ID_PROGRAM,
                MOD_CONTROL,
                VK_Q,
            ):
                logging.error("Failed to register Ctrl+Q hotkey")
                show_notification(APP_NAME, "Failed to register Ctrl+Q hotkey.")
            else:
                logging.info("Registered Ctrl+Q hotkey (PROGRAM)")

            # Register Ctrl + W → QUERY
            if not user32.RegisterHotKey(
                None,
                HOTKEY_ID_QUERY,
                MOD_CONTROL,
                VK_W,
            ):
                logging.error("Failed to register Ctrl+W hotkey")
                show_notification(APP_NAME, "Failed to register Ctrl+W hotkey.")
            else:
                logging.info("Registered Ctrl+W hotkey (QUERY)")

            msg = MSG()

            # Blocking message loop; exits when WM_QUIT posted
            while True:
                # GetMessageW returns:
                #  >0 for a message,
                #   0 for WM_QUIT,
                #  <0 for error
                result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if result == 0:  # WM_QUIT
                    break
                if result == -1:
                    logging.error("GetMessageW failed in hotkey loop")
                    break

                if msg.message == WM_HOTKEY:
                    hotkey_id = msg.wParam
                    if hotkey_id == HOTKEY_ID_PROGRAM:
                        self._process("program")
                    elif hotkey_id == HOTKEY_ID_QUERY:
                        self._process("query")

                # Optional: standard message translation/dispatch
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

        except Exception:
            logging.exception("Exception in hotkey loop")
        finally:
            # Always unregister on exit
            try:
                user32.UnregisterHotKey(None, HOTKEY_ID_PROGRAM)
            except Exception:
                pass
            try:
                user32.UnregisterHotKey(None, HOTKEY_ID_QUERY)
            except Exception:
                pass
            logging.info("Hotkey loop exited and hotkeys unregistered")

    def _stop_hotkey_thread(self):
        """
        Post WM_QUIT to the hotkey thread so GetMessageW stops blocking,
        then join the thread.
        """
        if self._hotkey_thread and self._hotkey_thread.is_alive():
            try:
                if self._hotkey_thread_id:
                    user32.PostThreadMessageW(
                        self._hotkey_thread_id,
                        WM_QUIT,
                        0,
                        0,
                    )
            except Exception:
                logging.exception("Failed to post WM_QUIT to hotkey thread")

            # Give the thread a moment to shut down
            self._hotkey_thread.join(timeout=2.0)

        self._hotkey_thread = None
        self._hotkey_thread_id = None

    # ==============================
    # Processing logic (unchanged)
    # ==============================
    def _process(self, which: str):
        # Run heavy work off the hotkey thread
        threading.Thread(
            target=self._process_thread,
            args=(which,),
            daemon=True,
        ).start()

    def _process_thread(self, which: str):
        # 1) Copy selected text
        txt = reliable_copy()
        if not txt or not txt.strip():
            return

        # 2) Length check
        if len(txt.split()) > MAX_WORDS:
            show_notification(APP_NAME, f"Input too long. Limit {MAX_WORDS} words.")
            return

        # 3) Pick mode
        mode_q, mode_w = self.get_modes()
        mode = mode_q if which == "program" else mode_w

        out = ""
        try:
            payload = {"text": txt, "mode": mode}
            r = api.post(POLISH_URL, payload, timeout=30)
            if r.status_code == 200:
                out = (r.json().get("text") or "").strip()
        except Exception:
            logging.exception("POLISH request failed")
            out = ""

        # 4) Fallback to original text
        if not out:
            out = txt.strip()

        # 5) Paste back
        pyperclip.copy(out)
        time.sleep(0.05)
        reliable_paste()
