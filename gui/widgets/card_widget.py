# Makes the card itself a reusable GUI component.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)


class CardWidget(QPushButton):

    def __init__(self, card, parent=None):
        super().__init__(parent)

        self.card = card
        self.selected = False

        self.setFixedSize(42, 68)

        self.setCursor(Qt.PointingHandCursor)

        # -------------------------------------------------
        # CARD CONTENT
        # -------------------------------------------------

        self.content = QWidget(self)
        self.content.setAttribute(
            Qt.WA_TransparentForMouseEvents
        )

        content_layout = QVBoxLayout(self.content)

        content_layout.setContentsMargins(
            2,
            2,
            2,
            2
        )

        content_layout.setSpacing(0)

        # -------------------------------------------------
        # TOP LEFT
        # -------------------------------------------------

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)

        self.top_label = QLabel(
            f"{card.rank.short}{card.suit.symbol}"
        )

        self.top_label.setAlignment(
            Qt.AlignLeft | Qt.AlignTop
        )

        top.addWidget(self.top_label)
        top.addStretch()

        content_layout.addLayout(top)

        # -------------------------------------------------
        # EMPTY SPACE
        # -------------------------------------------------

        content_layout.addStretch()

        # -------------------------------------------------
        # BOTTOM RIGHT
        # -------------------------------------------------

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)

        bottom.addStretch()

        self.bottom_label = QLabel(
            f"{card.rank.short}{card.suit.symbol}"
        )

        self.bottom_label.setAlignment(
            Qt.AlignRight | Qt.AlignBottom
        )

        bottom.addWidget(self.bottom_label)

        content_layout.addLayout(bottom)

        # -------------------------------------------------
        # POSITION CONTENT INSIDE BUTTON
        # -------------------------------------------------

        self.content.setGeometry(
            2,
            2,
            self.width() - 4,
            self.height() - 4
        )

        self.clicked.connect(
            self.toggle_selected
        )

        self.update_style()

    def resizeEvent(self, event):

        super().resizeEvent(event)

        self.content.setGeometry(
            2,
            2,
            self.width() - 4,
            self.height() - 4
        )

    def toggle_selected(self):

        self.selected = not self.selected

        self.update_style()

    def update_style(self):

        suit_name = self.card.suit.name

        if suit_name in ("HEARTS", "DIAMONDS"):
            suit_color = "#c5162e"
        else:
            suit_color = "#111111"

        border = (
            "#e5c557"
            if self.selected
            else "#aaa"
        )

        background = "#fffef7"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {background};

                border: 2px solid {border};
                border-radius: 6px;

                padding: 0px;
            }}

            QLabel {{
                color: {suit_color};

                font-size: 12px;
                font-weight: bold;

                background-color: transparent;
                border: none;

                padding: 0px;
            }}

            QPushButton:hover {{
                background-color: #f0eee3;
            }}
        """)