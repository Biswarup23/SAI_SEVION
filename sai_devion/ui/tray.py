from PyQt5 import QtWidgets, QtCore

class SystemTrayApp(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None, on_logout=None):
        super().__init__(icon, parent)
        self.setToolTip("SAI Devion")

        self._main_window = None
        self._on_logout = on_logout

        menu = QtWidgets.QMenu()

        open_action = menu.addAction("Open")
        open_action.triggered.connect(self._open_main)

        logout_action = menu.addAction("Logout")
        logout_action.triggered.connect(self._logout)

        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(QtWidgets.QApplication.quit)

        self.setContextMenu(menu)
        self.activated.connect(self._on_click)

    def set_main_window(self, win):
        self._main_window = win

    def _open_main(self):
        if self._main_window:
            self._main_window.showNormal()
            self._main_window.raise_()
            self._main_window.activateWindow()

    def _logout(self):
        # ✅ DO NOT quit app
        if callable(self._on_logout):
            self._on_logout()

    def _on_click(self, reason):
        if reason in (self.Trigger, self.DoubleClick):
            self._open_main()
