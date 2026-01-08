from PyQt5 import QtWidgets, QtCore
from sai_devion.session_store import Profile
from sai_devion.config import APP_NAME


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, profile: Profile):
        super().__init__()
        self.profile = profile

        self.setWindowTitle("⚙ Settings")
        self.setFixedSize(420, 320)
        # self.setStyleSheet("""
        #     QDialog { background:#ffffff; color:#111; font-family:'Segoe UI'; }
        #     QLabel { color:#111; }
        #     QPushButton { padding:8px; border-radius:6px; background:#e5e7eb; }
        #     QPushButton:hover { background:#d1d5db; }
        # """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        full_name = " ".join([x for x in [
            profile.first_name,
            profile.middle_name or "",
            profile.last_name or ""
        ] if x]).strip()

        info = (
            f"App: {APP_NAME}\n\n"
            f"Name: {full_name or '-'}\n"
            f"Email: {profile.email or '-'}\n"
            f"Contact: {profile.contact_number or '-'}\n"
            f"Occupation: {profile.occupation or '-'}\n"
            f"Country: {profile.country or '-'}\n"
            f"Subscription: {'Pro' if profile.subscription == 1 else 'Free'}"
        )

        lbl = QtWidgets.QLabel(info)
        # lbl.setStyleSheet("background:#f3f4f6;padding:12px;border-radius:8px;")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignCenter)
