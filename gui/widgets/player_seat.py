#displays one player's hand.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
)

from .card_widget import CardWidget


class PlayerSeat(QFrame):

    def __init__(
        self,
        player,
        role="",
        active=False,
        parent=None,
    ):
        super().__init__(parent)

        self.player = player
        self.role = role
        self.active = active

        self.setup_ui()

    def setup_ui(self):

        self.setObjectName("playerSeat")

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            12,
            10,
            12,
            10
        )

        layout.setSpacing(8)

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = QHBoxLayout()

        position = QLabel(
            self.player.position.value
        )

        position.setStyleSheet("""
            color: #e5c557;
            font-size: 14px;
            font-weight: bold;
        """)

        header.addWidget(position)

        if self.role:

            role_label = QLabel(
                self.role.upper()
            )

            role_label.setStyleSheet("""
                color: #e5c557;
                font-size: 12px;
                letter-spacing: 1px;
            """)

            header.addWidget(role_label)

        header.addStretch()

        card_count = QLabel(
            f"{len(self.player.hand)} CARDS"
        )

        card_count.setStyleSheet("""
            color: #aebbb5;
            font-size: 12px;
        """)

        header.addWidget(card_count)

        layout.addLayout(header)

        # -------------------------------------------------
        # HAND
        # -------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setFrameShape(QFrame.NoFrame)

        hand_widget = QFrame()

        hand_layout = QHBoxLayout(hand_widget)

        hand_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        hand_layout.setSpacing(-7)

        for card in self.player.hand.sorted_by_suit():

            card_widget = CardWidget(card)

            hand_layout.addWidget(card_widget)

        hand_layout.addStretch()

        scroll.setWidget(hand_widget)

        layout.addWidget(scroll)

        self.setStyleSheet(self.get_style())

    def get_style(self):

        if self.active:

            return """
                QFrame#playerSeat {
                    background-color: #00582b;
                    border: 3px solid #e5c557;
                    border-radius: 10px;
                }
            """

        return """
            QFrame#playerSeat {
                background-color: #00582b;
                border: 1px solid transparent;
                border-radius: 10px;
            }
        """