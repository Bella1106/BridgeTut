#keeps the other navigation buttons working while we build them later.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
)


class PlaceholderPage(QWidget):

    def __init__(
        self,
        title,
        message,
    ):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            16,
            16,
            16
        )

        panel = QFrame()

        panel.setStyleSheet("""
            QFrame {
                background-color: #00602e;
                border-radius: 12px;
            }
        """)

        panel_layout = QVBoxLayout(panel)

        panel_layout.setAlignment(
            Qt.AlignCenter
        )

        title_label = QLabel(title)

        title_label.setStyleSheet("""
            color: #e5c557;
            font-family: Georgia, serif;
            font-size: 38px;
            font-weight: bold;
        """)

        title_label.setAlignment(
            Qt.AlignCenter
        )

        message_label = QLabel(message)

        message_label.setStyleSheet("""
            color: #d9ebe3;
            font-size: 17px;
        """)

        message_label.setAlignment(
            Qt.AlignCenter
        )

        panel_layout.addWidget(title_label)
        panel_layout.addWidget(message_label)

        layout.addWidget(panel)