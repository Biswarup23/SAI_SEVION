# sai_devion/ui/feedback_dialog.py
import platform
from PyQt5 import QtWidgets, QtCore

from sai_devion.config import VERSION


class FeedbackDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Remove "?" from title bar
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.setWindowTitle("Send Feedback")
        self.setModal(True)
        self.resize(420, 360)

        # ===== Root layout =====
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        # Global style for dialog
        self.setStyleSheet("""
            QDialog {
                background: #F9FAFB;
                color: #111827;
                font-family: "Segoe UI";
                font-size: 12px;
            }
            QLabel {
                color: #111827;
            }
            QComboBox, QSpinBox, QTextEdit {
                background: #FFFFFF;
                border: 1px solid #D1D5DB;
                border-radius: 6px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QTextEdit {
                min-height: 80px;
            }
            QPushButton {
                background: #111827;
                color: #F9FAFB;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #374151;
            }
            QPushButton:pressed {
                background: #000000;
            }
        """)

        # ===== Title =====
        title = QtWidgets.QLabel("We’d love to hear your feedback 🙌")
        title.setWordWrap(True)
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: 600;")
        layout.addWidget(title)

        # ===== Card frame for form =====
        form_frame = QtWidgets.QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
            }
        """)
        form_layout = QtWidgets.QVBoxLayout(form_frame)
        form_layout.setContentsMargins(12, 12, 12, 12)
        form_layout.setSpacing(8)

        # Category
        cat_label = QtWidgets.QLabel("Category:")
        self.category_combo = QtWidgets.QComboBox()
        self.category_combo.addItems(["bug", "idea", "ui", "performance", "other"])
        form_layout.addWidget(cat_label)
        form_layout.addWidget(self.category_combo)

        # Rating
        rating_label = QtWidgets.QLabel("Rating (1–5):")
        self.rating_spin = QtWidgets.QSpinBox()
        self.rating_spin.setRange(1, 5)
        self.rating_spin.setValue(5)
        form_layout.addWidget(rating_label)
        form_layout.addWidget(self.rating_spin)

        # Message
        msg_label = QtWidgets.QLabel("Message:")
        self.message_edit = QtWidgets.QTextEdit()
        self.message_edit.setPlaceholderText("Tell us what’s working well or what we should improve…")
        form_layout.addWidget(msg_label)
        form_layout.addWidget(self.message_edit, 1)

        layout.addWidget(form_frame)

        # Platform (readonly)
        plat = f"{platform.system()} {platform.release()}"
        self.platform_label = QtWidgets.QLabel(f"Platform: {plat} | App: v{VERSION}")
        self.platform_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        layout.addWidget(self.platform_label)

        # Buttons
        btn_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok |
                                             QtWidgets.QDialogButtonBox.Cancel)
        # Style only the buttons inside the button box
        for btn in btn_box.buttons():
            btn.setCursor(QtCore.Qt.PointingHandCursor)

        btn_box.accepted.connect(self._on_accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box, alignment=QtCore.Qt.AlignRight)

        self._app_version = VERSION
        self._platform = plat

    def _on_accept(self):
        text = self.message_edit.toPlainText().strip()
        if not text:
            QtWidgets.QMessageBox.warning(self, "Feedback", "Please write some feedback before sending.")
            return
        self.accept()

    def build_payload(self, user_email: str | None = None):
        return {
            "message": self.message_edit.toPlainText().strip(),
            "rating": self.rating_spin.value(),
            "category": self.category_combo.currentText(),
            "app_version": self._app_version,
            "platform": self._platform,
            "user_email": user_email,
        }
