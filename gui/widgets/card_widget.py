#Makes the card itself a reusable GUI component.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


class CardWidget(QPushButton):

    def __init__(self, card, parent=None):
        super().__init__(parent)

        self.card = card
        self.selected = False

        self.setFixedSize(42, 68)

        self.setText(
            f"{card.rank.short}\n{card.suit.symbol}"
        )

        self.setCursor(Qt.PointingHandCursor)

        self.clicked.connect(self.toggle_selected)

        self.update_style()

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

                color: {suit_color};

                border: 2px solid {border};
                border-radius: 6px;

                font-size: 13px;
                font-weight: bold;

                padding: 3px;
            }}

            QPushButton:hover {{
                background-color: #f0eee3;
            }}
        """)