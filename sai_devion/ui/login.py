from PyQt5 import QtWidgets
from sai_devion.auth_service import AuthService
from sai_devion.session_store import SessionStore
from sai_devion.config import APP_NAME
from sai_devion.ui.signup import SignupWindow


class LoginWindow(QtWidgets.QDialog):
    def __init__(self, auth: AuthService, store: SessionStore):
        super().__init__()
        self.auth = auth
        self.store = store

        self.setWindowTitle(f"{APP_NAME} - Login")
        self.setFixedSize(350, 250)
        self.setStyleSheet("background:#FFF; font-family:Segoe UI;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet(
            "padding:8px;border:1px solid #444;border-radius:6px;background:#c0c3c4;color:#000;"
        )
        layout.addWidget(self.email_input)

        self.pass_input = QtWidgets.QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pass_input.setStyleSheet(
            "padding:8px;border:1px solid #444;border-radius:6px;background:#c0c3c4;color:#000;"
        )
        layout.addWidget(self.pass_input)

        btn_layout = QtWidgets.QHBoxLayout()

        self.login_btn = QtWidgets.QPushButton("🔑 Login")
        self.login_btn.setStyleSheet("background:#60abc4;color:#000;padding:6px 12px;border-radius:6px;")
        self.login_btn.clicked.connect(self.check_login)
        btn_layout.addWidget(self.login_btn)

        self.signup_btn = QtWidgets.QPushButton("📝 Sign up")
        self.signup_btn.setStyleSheet("background:#60abc4;color:#000;padding:6px 12px;border-radius:6px;")
        self.signup_btn.clicked.connect(self.open_signup)
        btn_layout.addWidget(self.signup_btn)

        layout.addLayout(btn_layout)

        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color:#000; margin-top:8px; font-size:11px;")
        layout.addWidget(self.status)

    def open_signup(self):
        dlg = SignupWindow(self.auth)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            # Signup success -> user must verify email; stay on login page
            QtWidgets.QMessageBox.information(
                self,
                "Signup successful",
                "Account created. Please verify your email, then login."
            )

    def check_login(self):
        email = self.email_input.text().strip()
        password = self.pass_input.text().strip()

        if not email or not password:
            self.status.setText("⚠️ Enter email and password")
            return

        ok, msg = self.auth.login(email, password, self.store)
        if ok:
            self.accept()
        else:
            self.status.setText(f"❌ {msg}")
