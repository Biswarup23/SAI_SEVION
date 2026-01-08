import threading, time, logging
import pyperclip, keyboard

from sai_devion.utils.clipboard import reliable_copy, reliable_paste
from sai_devion.utils.notifications import show_notification
from sai_devion.config import APP_NAME, HOTKEY1, HOTKEY2, MAX_WORDS, POLISH_URL
from sai_devion.api_client import api
from sai_devion.session_store import SessionStore

class HotkeyHandler:
    def __init__(self, store: SessionStore, get_modes_callable):
        """
        get_modes_callable should return (mode_q, mode_w)
        where mode_q is dict for Ctrl+Q (PROGRAM), mode_w for Ctrl+W (QUERY)
        """
        self.store = store
        self.get_modes = get_modes_callable

    def register_hotkeys(self):
        try:
            try:
                keyboard.unhook_all_hotkeys()
            except Exception:
                pass

            keyboard.add_hotkey(HOTKEY1, lambda: self._process(HOTKEY1), suppress=True)
            keyboard.add_hotkey(HOTKEY2, lambda: self._process(HOTKEY2), suppress=True)

            mode_q, mode_w = self.get_modes()
            show_notification(
                APP_NAME,
                f"Hotkeys enabled:\nCtrl+Q → PROGRAM ({mode_q['lang']})\nCtrl+W → QUERY ({mode_w['lang']})"
            )
        except Exception as e:
            logging.exception("Hotkey registration failed")
            show_notification(APP_NAME, f"Hotkey registration failed. Run as Admin if needed.\n{e}")

    def _process(self, hotkey):
        threading.Thread(target=self._process_thread, args=(hotkey,), daemon=True).start()

    def _process_thread(self, hotkey):
        txt = reliable_copy()
        if not txt or not txt.strip():
            return

        if len(txt.split()) > MAX_WORDS:
            show_notification(APP_NAME, f"Input too long. Limit {MAX_WORDS} words.")
            return

        mode_q, mode_w = self.get_modes()
        mode = mode_q if hotkey == HOTKEY1 else mode_w

        out = ""
        try:
            payload = {"text": txt, "mode": mode}
            r = api.post(POLISH_URL, payload, timeout=30)
            if r.status_code == 200:
                out = (r.json().get("text") or "").strip()
        except Exception:
            out = ""

        if not out:
            out = txt.strip()

        pyperclip.copy(out)
        time.sleep(0.05)
        reliable_paste()
