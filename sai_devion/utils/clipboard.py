import time, logging
import pyperclip, keyboard

def reliable_copy(timeout=2.0, poll_interval=0.05):
    for k in ("ctrl", "alt", "shift"):
        try: keyboard.release(k)
        except Exception as e:
            logging.exception(f"Failed to release key '{k}': {e}")
            print(f"Failed to release key '{k}': {e}")

    time.sleep(0.03)

    prev = pyperclip.paste()
    try:
        keyboard.press_and_release("ctrl+c")
    except Exception:
        logging.exception("Keyboard copy failed")
    for k in ("ctrl", "alt", "shift"):
        try: keyboard.release(k)
        except Exception as e:
            logging.exception(f"Failed to release key '{k}': {e}")
            print(f"Failed to release key '{k}': {e}")

    waited = 0.0
    new = pyperclip.paste()
    while waited < timeout and new == prev:
        time.sleep(poll_interval)
        waited += poll_interval
        new = pyperclip.paste()
    return new

def reliable_paste():
    for k in ("ctrl", "alt", "shift"):
        try: keyboard.release(k)
        except Exception as e:
            logging.exception(f"Failed to release key '{k}': {e}")
            print(f"Failed to release key '{k}': {e}")

    time.sleep(0.03)
    try:
        keyboard.press_and_release("ctrl+v")
    except Exception:
        logging.exception("Keyboard paste failed")
    for k in ("ctrl", "alt", "shift"):
        try: keyboard.release(k)
        except Exception as e:
            logging.exception(f"Failed to release key '{k}': {e}")
            print(f"Failed to release key '{k}': {e}")
