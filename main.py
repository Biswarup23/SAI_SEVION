import sys
from PyQt5 import QtWidgets, QtGui, QtCore

from sai_devion.utils.logging_setup import setup_logging
from sai_devion.session_store import SessionStore
from sai_devion.config import ICON_LOGO_REL
from sai_devion.auth_http import HttpAuthService
from sai_devion.ui.login import LoginWindow
from sai_devion.ui.main_window import MainWindow
from sai_devion.ui.tray import SystemTrayApp
from sai_devion.utils.resources import resource_path


class AppController(QtCore.QObject):
    def __init__(self, app: QtWidgets.QApplication):
        super().__init__()
        self.app = app
        self.app.setQuitOnLastWindowClosed(False)

        self.store = SessionStore()
        self.auth = HttpAuthService()

        self.main_win: MainWindow | None = None
        self.tray: SystemTrayApp | None = None

    def start(self):
        profile = self.auth.try_auto_login(self.store)

        # Auto-login only makes sense if we already have tray/main state.
        # We create tray AFTER a successful login (or auto-login).
        if profile:
            self._ensure_tray()
            self.show_main(profile)
        else:
            self.show_login()

    def _ensure_tray(self):
        """Create tray only once, only after login."""
        if self.tray is None:
            tray_icon = QtGui.QIcon(resource_path(ICON_LOGO_REL))
            self.tray = SystemTrayApp(tray_icon, parent=None, on_logout=self.logout_full)
            self.tray.show()

            # If main window already exists, connect tray "Open" to it
            if self.main_win:
                self.tray.set_main_window(self.main_win)

    def show_login(self):
        """
        Show login dialog.
        - If login success: create tray + show main
        - If cancel: exit app (because you don't want tray when logged out)
        """
        login = LoginWindow(auth=self.auth, store=self.store)
        result = login.exec_()

        if result == QtWidgets.QDialog.Accepted:
            profile = self.store.get_profile()
            if profile:
                self._ensure_tray()
                self.show_main(profile)
                return

        # user cancelled -> exit completely (no tray in logged-out state)
        QtWidgets.QApplication.quit()

    def show_main(self, profile):
        """
        Create or refresh main window and show it.
        """
        if self.main_win is None:
            self.main_win = MainWindow(
                auth=self.auth,
                store=self.store,
                profile=profile,
                on_logout=self.logout_full
            )
        else:
            self.main_win.set_profile(profile)

        # Link tray Open action to main window
        if self.tray:
            self.tray.set_main_window(self.main_win)

        self.main_win.show()
        self.main_win.raise_()
        self.main_win.activateWindow()

    def logout_full(self):
        """
        Full sign-out:
        - Clear all session
        - Hide main window
        - Remove tray icon
        - Show login again (fresh)
        """
        # 1) clear session (profile + refresh token + access token)
        self.auth.logout(self.store)  # calls store.clear_all()

        # 2) hide main window
        if self.main_win:
            self.main_win.hide()

        # 3) remove tray icon completely (you requested this)
        if self.tray:
            self.tray.hide()
            self.tray.setContextMenu(None)
            self.tray.deleteLater()
            self.tray = None

        # 4) show login again
        QtCore.QTimer.singleShot(150, self.show_login)


def main():
    setup_logging()
    app = QtWidgets.QApplication(sys.argv)

    controller = AppController(app)
    controller.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
