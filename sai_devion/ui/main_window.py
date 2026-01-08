import os, json
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QIcon
import requests

from sai_devion.config import APP_NAME, VERSION, HOTKEY1, HOTKEY2
from sai_devion.utils.resources import resource_path
from sai_devion.config import ICON_ICO_REL, ICON_LOGO_REL
from sai_devion.utils.notifications import show_notification
from sai_devion.utils.hotkeys import HotkeyHandler
from sai_devion.ui.dialogs import hotkeys_dialog, help_dialog
from sai_devion.ui.settings_dialog import SettingsDialog
from sai_devion.ui.feedback_dialog import FeedbackDialog
# if you have your own API client:
from sai_devion.api_client import api  # adjust if needed


class MainWindow(QtWidgets.QWidget):
    def __init__(self, auth, store, profile, on_logout=None):
        super().__init__()
        self.auth = auth
        self.store = store
        self.profile = profile
        self._on_logout = on_logout

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(resource_path(ICON_ICO_REL)))
        self.setFixedSize(650, 650)
        self.setStyleSheet("background-color:#FFFFFF; color:#000; font-family:Segoe UI;")

        self.mode_config_file = self._mode_config_path()

        # Modes (defaults)
        self.mode_q = {"action": "Program", "lang": "Python"}  # Ctrl+Q
        self.mode_w = {"action": "Query", "lang": "Mysql"}     # Ctrl+W
        self._load_mode_config()

        self.hotkeys = HotkeyHandler(store=self.store, get_modes_callable=self.get_modes)

        self._build_ui()
        self.hotkeys.register_hotkeys()
    #
    # def _mode_config_path(self):
    #     # store alongside session file dir for production cleanliness
    #     data_dir = os.path.dirname(self.store.session_file)
    #     return os.path.join(data_dir, "mode_config.json")
    #
    # def closeEvent(self, event):
    #     event.ignore()
    #     self.hide()
    #     show_notification(APP_NAME, "SAI Devion is running in tray.")
    #
    # def _save_mode_config(self):
    #     with open(self.mode_config_file, "w", encoding="utf-8") as f:
    #         json.dump({
    #             "query_lang": self.mode_w["lang"],
    #             "program_lang": self.mode_q["lang"]
    #         }, f, ensure_ascii=False, indent=2)
    #
    # def _load_mode_config(self):
    #     try:
    #         if os.path.exists(self.mode_config_file):
    #             with open(self.mode_config_file, "r", encoding="utf-8") as f:
    #                 cfg = json.load(f)
    #             self.mode_w["lang"] = cfg.get("query_lang", self.mode_w["lang"])
    #             self.mode_q["lang"] = cfg.get("program_lang", self.mode_q["lang"])
    #     except Exception:
    #         pass
    #
    def _mode_config_path(self):
        # store alongside session file dir for production cleanliness
        data_dir = os.path.dirname(self.store.session_file)
        return os.path.join(data_dir, "mode_config.json")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        show_notification(APP_NAME, "SAI Devion is running in tray.")

    def _save_mode_config(self):
        os.makedirs(os.path.dirname(self.mode_config_file), exist_ok=True)
        with open(self.mode_config_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "query_lang": self.mode_w["lang"],
                    "program_lang": self.mode_q["lang"],
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

    def _load_mode_config(self):
        try:
            if os.path.exists(self.mode_config_file):
                with open(self.mode_config_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self.mode_w["lang"] = cfg.get("query_lang", self.mode_w["lang"])
                self.mode_q["lang"] = cfg.get("program_lang", self.mode_q["lang"])
        except Exception:
            pass
    def get_modes(self):
        return self.mode_q, self.mode_w

    def _build_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # LEFT PANEL
        self.left_panel = QtWidgets.QFrame()
        self.left_panel.setFixedWidth(280)
        self.left_panel.setStyleSheet("""
            QFrame { background-color:#F9FAFB; border-right:1px solid #E5E7EB; padding:20px; }
        """)
        left_layout = QtWidgets.QVBoxLayout(self.left_panel)

        display_name = (self.profile.first_name or "User").strip()
        self.avatar_lbl = QtWidgets.QLabel(display_name[:1].upper())
        self.avatar_lbl.setFixedSize(64, 64)
        self.avatar_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.avatar_lbl.setStyleSheet("""
            background-color:#60A5FA; color:white; font-size:28px;
            font-weight:bold; border-radius:32px;
        """)
        left_layout.addWidget(self.avatar_lbl, alignment=QtCore.Qt.AlignCenter)

        self.username_lbl = QtWidgets.QLabel(display_name)
        self.username_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.username_lbl.setWordWrap(True)
        self.username_lbl.setStyleSheet("""
            font-size:14px;font-weight:500;color:#111827;background-color:#E5E7EB;
            padding:12px;border-radius:8px;margin-top:8px;
        """)
        left_layout.addWidget(self.username_lbl)

        self.subscription_lbl = QtWidgets.QLabel(f"⭐ {'Pro' if self.profile.subscription==1 else 'Free'} | V-{VERSION}")
        self.subscription_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.subscription_lbl.setStyleSheet("color:#6B7280;font-size:13px;margin-top:4px;")
        left_layout.addWidget(self.subscription_lbl)

        button_style = """
        QPushButton { background-color:#1F2937; color:#F3F4F6; padding:8px 12px;
                      border-radius:6px; font-size:14px; margin-top:6px; }
        QPushButton:hover { background-color:#374151; }
        """

        btn_hotkeys = QtWidgets.QPushButton("⚡ Hotkeys")
        btn_hotkeys.setStyleSheet(button_style)
        btn_hotkeys.clicked.connect(lambda: hotkeys_dialog(self))
        left_layout.addWidget(btn_hotkeys)

        btn_settings = QtWidgets.QPushButton("⚙ Settings")
        btn_settings.setStyleSheet(button_style)
        btn_settings.clicked.connect(lambda: SettingsDialog(self.profile).exec_())
        left_layout.addWidget(btn_settings)

        btn_help = QtWidgets.QPushButton("❓ Help")
        btn_help.setStyleSheet(button_style)
        btn_help.clicked.connect(lambda: help_dialog(self))
        left_layout.addWidget(btn_help)

        # 📝 FEEDBACK BUTTON
        btn_feedback = QtWidgets.QPushButton("📝 Feedback")
        btn_feedback.setStyleSheet(button_style)
        btn_feedback.clicked.connect(self.open_feedback_dialog)
        left_layout.addWidget(btn_feedback)


        btn_logout = QtWidgets.QPushButton("🔓 Logout")
        btn_logout.setStyleSheet(button_style)
        btn_logout.clicked.connect(self._logout_clicked)
        left_layout.addWidget(btn_logout)

        left_layout.addStretch()
        main_layout.addWidget(self.left_panel)

        # RIGHT PANEL
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)

        # Logo + title
        top = QtWidgets.QVBoxLayout()
        top.setContentsMargins(0, 0, 0, 110)

        logo = QtWidgets.QLabel()
        logo_path = resource_path(ICON_LOGO_REL)
        if os.path.exists(logo_path):
            pix = QtGui.QPixmap(logo_path)
            logo.setPixmap(pix.scaled(300, 500, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        logo.setAlignment(QtCore.Qt.AlignCenter)
        logo.setStyleSheet("background:#FFF;border-radius:12px;padding:10px;")
        top.addWidget(logo, alignment=QtCore.Qt.AlignHCenter)

        title = QtWidgets.QLabel("SAI Devion")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("color:#000;font-size:26px;font-weight:bold;letter-spacing:1px;")
        top.addWidget(title, alignment=QtCore.Qt.AlignHCenter)

        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setStyleSheet("color:#2c2c3a;")
        top.addWidget(sep)

        right_layout.addLayout(top)
        box = QtWidgets.QVBoxLayout()

        # ---- QUERY ----
        self.lbl_query = QtWidgets.QLabel(f"QUERY ({HOTKEY2})")
        self.lbl_query.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #111827;
                margin-top: 4px;
            }
        """)

        self.combo_query = QtWidgets.QComboBox()
        self.combo_query.addItems([
            "Mysql", "PostgreSQL", "SQLite", "Oracle",
            "SQL Server", "MariaDB", "Snowflake",
            "BigQuery", "Redshift", "MongoDB"
        ])
        self._style_combo(self.combo_query)

        # ---- PROGRAM ----
        self.lbl_program = QtWidgets.QLabel(f"PROGRAMMING ({HOTKEY1})")
        self.lbl_program.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #111827;
                margin-top: 4px;
            }
        """)

        self.combo_program = QtWidgets.QComboBox()
        self.combo_program.addItems([
            "Python", "Java", "C", "C++", "C#", "JavaScript",
            "TypeScript", "Go", "Rust", "PHP", "Ruby",
            "Swift", "Kotlin", "R", "Scala", "Dart"
        ])
        self._style_combo(self.combo_program)
        # ✅ Apply saved choices to UI (important)
        self.combo_query.setCurrentText(self.mode_w["lang"])
        self.combo_program.setCurrentText(self.mode_q["lang"])
        # ---------- LAYOUT ----------
        box = QtWidgets.QVBoxLayout()  # ✅ THIS LINE FIXES THE ERROR

        box.addWidget(self.lbl_query)
        box.addWidget(self.combo_query)
        box.addSpacing(10)
        box.addWidget(self.lbl_program)
        box.addWidget(self.combo_program)

        frame = QtWidgets.QFrame()
        frame.setLayout(box)
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                background-color: #FFFFFF;
                padding: 12px;
            }
        """)

        right_layout.addWidget(frame)

        self.status_lbl = QtWidgets.QLabel(
            "Ready. Select text and press hotkeys.\nWrite your logic after $^ — SAI will generate the code or query for you."
        )
        self.status_lbl.setWordWrap(True)
        self.status_lbl.setFixedHeight(100)
        self.status_lbl.setFixedWidth(350)
        self.status_lbl.setStyleSheet("background:#b7bbbd;padding:15px;border-radius:8px;")
        right_layout.addWidget(self.status_lbl)

        self.save_btn = QtWidgets.QPushButton("💾 Save Choice & Hotkeys")
        self.save_btn.setStyleSheet("""
            QPushButton { background:#6db1cf;color:#2c383d;border-radius:8px;font-size:14px;font-weight:bold;padding:8px 14px; }
            QPushButton:hover { background:#5eb9e0; }
            QPushButton:pressed { background:#19a8e6; }
        """)
        self.save_btn.clicked.connect(self.save_choice)
        right_layout.addWidget(self.save_btn)

        main_layout.addWidget(right_panel)

    def _style_combo(self, combo):
        combo.setStyleSheet("""
            QComboBox { background:#FFF;color:#000;padding:6px;border:1px solid #03A9F4;border-radius:6px; }
            QComboBox::drop-down { border:none;background:#d5e2e8;width:24px; }
            QComboBox QAbstractItemView { background:#FFF; selection-background-color:#d5e2e8; selection-color:#000; }
        """)

    def save_choice(self):
        self.mode_w = {"action": "Query", "lang": self.combo_query.currentText()}
        self.mode_q = {"action": "Program", "lang": self.combo_program.currentText()}

        self._save_mode_config()

        show_notification(APP_NAME, f"Saved:\nQUERY → {self.mode_w['lang']}\nPROGRAM → {self.mode_q['lang']}")
        self.hotkeys.register_hotkeys()
    def open_feedback_dialog(self):
        dlg = FeedbackDialog(self)

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            # logged-in user's email from session/profile
            user_email = getattr(self.profile, "email", None)

            payload = dlg.build_payload(user_email=user_email)

            try:
                BASE_URL = "http://127.0.0.1:8000/api/v1"
                url = f"{BASE_URL}/feedback"

                resp = requests.post(url, json=payload, timeout=10)
                resp.raise_for_status()

                data = resp.json()
                show_notification(APP_NAME, "Thank you for your feedback! 💙")

            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Feedback Error",
                    f"Failed to send feedback:\n{e}",
                )


    def do_logout(self):
        if callable(self._on_logout):
            self._on_logout()
        else:
            # fallback safety
            self.auth.logout(self.store)
            self.hide()

    def _logout_clicked(self):
        if callable(self._on_logout):
            self._on_logout()
        else:
            # fallback
            self.auth.logout(self.store)
            self.hide()

    def set_profile(self, profile):
        self.profile = profile

        display_name = (self.profile.first_name or "User").strip()

        # update username + avatar
        self.username_lbl.setText(display_name)
        self.avatar_lbl.setText(display_name[:1].upper() if display_name else "U")

        # update subscription label
        self.subscription_lbl.setText(
            f"⭐ {'Pro' if self.profile.subscription == 1 else 'Free'} | V-{VERSION}"
        )
