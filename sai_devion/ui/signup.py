from PyQt5 import QtWidgets
from sai_devion.auth_service import AuthService
from sai_devion.utils.notifications import show_notification
from sai_devion.config import APP_NAME

class SignupWindow(QtWidgets.QDialog):
    def __init__(self, auth: AuthService):
        super().__init__()
        self.auth = auth
        self.setWindowTitle(f"{APP_NAME} - Sign up")
        self.setFixedSize(520, 520)
        self.setStyleSheet("background:#FFF; color:#111; font-family:Segoe UI;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        def mk_line(ph):
            e = QtWidgets.QLineEdit()
            e.setPlaceholderText(ph)
            e.setStyleSheet("padding:8px;border:1px solid #bbb;border-radius:6px;background:#f3f4f6;color:#111;")
            return e

        self.first_name = mk_line("First name")
        self.middle_name = mk_line("Middle name (optional)")
        self.last_name = mk_line("Last name")
        self.contact = mk_line("Contact number")
        self.email = mk_line("Email")

        self.occupation = QtWidgets.QComboBox()
        self.occupation.addItems(["student", "professional", "other"])
        self.occupation.setStyleSheet("padding:8px;border:1px solid #bbb;border-radius:6px;background:#f3f4f6;color:#111;")

        self.country = mk_line("Country")

        self.password = mk_line("Password (min 8 chars)")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm = mk_line("Confirm password")
        self.confirm.setEchoMode(QtWidgets.QLineEdit.Password)

        for w in [self.first_name, self.middle_name, self.last_name, self.contact, self.email, self.occupation, self.country, self.password, self.confirm]:
            layout.addWidget(w)

        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color:#111; font-size:11px;")
        layout.addWidget(self.status)

        btns = QtWidgets.QHBoxLayout()
        self.create_btn = QtWidgets.QPushButton("Create account")
        self.create_btn.setStyleSheet("background:#60abc4;color:#000;padding:8px;border-radius:6px;")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.cancel_btn.setStyleSheet("background:#e5e7eb;color:#111;padding:8px;border-radius:6px;")
        btns.addWidget(self.create_btn)
        btns.addWidget(self.cancel_btn)
        layout.addLayout(btns)

        self.cancel_btn.clicked.connect(self.reject)
        self.create_btn.clicked.connect(self._signup)

    def _signup(self):
        fn = self.first_name.text().strip()
        ln = self.last_name.text().strip()
        ct = self.contact.text().strip()
        em = self.email.text().strip()
        oc = self.occupation.currentText().strip()
        co = self.country.text().strip()
        pw = self.password.text()
        cf = self.confirm.text()

        if not fn or not ln or not ct or not em or not oc or not co or not pw:
            self.status.setText("⚠ Please fill all required fields.")
            return
        if len(pw) < 8:
            self.status.setText("⚠ Password must be at least 8 characters.")
            return
        if pw != cf:
            self.status.setText("⚠ Passwords do not match.")
            return


        payload = {
            "first_name": fn,
            "middle_name": self.middle_name.text().strip() or None,
            "last_name": ln,
            "contact_number": ct,
            "email": em,
            "occupation": oc,
            "country": co,
            "password": pw
        }

        ok, msg = self.auth.signup(payload)
        if ok:
            show_notification(APP_NAME, msg)
            self.accept()
        else:
            self.status.setText(f"❌ {msg}")
