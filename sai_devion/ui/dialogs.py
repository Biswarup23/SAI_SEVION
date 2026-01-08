from PyQt5 import QtWidgets, QtCore
from sai_devion.config import APP_NAME

def hotkeys_dialog(parent):
    d = QtWidgets.QDialog(parent, flags=QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
    d.setWindowTitle("⚡ Hotkeys")
    d.setFixedSize(350, 200)
    d.setStyleSheet("background:#a0a9ad;color:#000;font-family:'Segoe UI';")
    layout = QtWidgets.QVBoxLayout(d)
    label = QtWidgets.QLabel("Hotkeys:\n\n- Ctrl+Q → PROGRAM\n- Ctrl+W → QUERY")
    label.setWordWrap(True)
    label.setStyleSheet("background:#E5E7EB;border-radius:6px;padding:12px;")
    layout.addWidget(label)
    btn = QtWidgets.QPushButton("Close")
    btn.clicked.connect(d.close)
    layout.addWidget(btn, alignment=QtCore.Qt.AlignCenter)
    d.exec_()

def settings_dialog(parent, profile):
    d = QtWidgets.QDialog(parent, flags=QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
    d.setWindowTitle("⚙ Settings")
    d.setFixedSize(360, 220)
    d.setStyleSheet("background:#a0a9ad;color:#000;font-family:'Segoe UI';")
    layout = QtWidgets.QVBoxLayout(d)
    text = f"{APP_NAME}\n\nName: {profile.first_name}\nEmail: {profile.email or '-'}\nSubscription: {'Pro' if profile.subscription == 1 else 'Free'}"
    label = QtWidgets.QLabel(text)
    label.setWordWrap(True)
    label.setStyleSheet("background:#E5E7EB;border-radius:6px;padding:12px;")
    layout.addWidget(label)
    btn = QtWidgets.QPushButton("Close")
    btn.clicked.connect(d.close)
    layout.addWidget(btn, alignment=QtCore.Qt.AlignCenter)
    d.exec_()

def help_dialog(parent):
    d = QtWidgets.QDialog(parent, flags=QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
    d.setWindowTitle("❓ Help")
    d.setFixedSize(350, 200)
    d.setStyleSheet("background:#a0a9ad;color:#000;font-family:'Segoe UI';")
    layout = QtWidgets.QVBoxLayout(d)
    label = QtWidgets.QLabel("If issues persist, contact:\nsupport@saigroups.co.uk")
    label.setWordWrap(True)
    label.setStyleSheet("background:#E5E7EB;border-radius:6px;padding:12px;")
    layout.addWidget(label)
    btn = QtWidgets.QPushButton("Close")
    btn.clicked.connect(d.close)
    layout.addWidget(btn, alignment=QtCore.Qt.AlignCenter)
    d.exec_()
