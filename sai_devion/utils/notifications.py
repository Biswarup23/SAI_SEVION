import os, platform, threading, logging
from sai_devion.utils.resources import resource_path
from sai_devion.config import ICON_ICO_REL

def _notify(title: str, msg: str):
    icon = resource_path(ICON_ICO_REL)
    icon = icon if os.path.exists(icon) else None
    system = platform.system()

    try:
        if system == "Windows":
            try:
                from win11toast import toast
                toast(title, msg, icon=icon, duration="short")
                return
            except Exception:
                pass

            try:
                from plyer import notification
                notification.notify(title=title, message=msg, timeout=3, app_icon=icon)
                return
            except Exception:
                pass

            try:
                from win10toast_click import ToastNotifier
                ToastNotifier().show_toast(title, msg, icon_path=icon, duration=3)
                return
            except Exception as e:
                logging.warning(f"Windows toast failed: {e}")

        elif system == "Darwin":
            import os as _os
            _os.system(f'''osascript -e 'display notification "{msg}" with title "{title}"' ''')
            return

        elif system == "Linux":
            import os as _os
            _os.system(f'notify-send "{title}" "{msg}"')
            return

        print(f"[NOTIFY] {title}: {msg}")
    except Exception as e:
        logging.warning(f"Notification failed: {e}")

def show_notification(title: str, msg: str):
    threading.Thread(target=_notify, args=(title, msg), daemon=True).start()
