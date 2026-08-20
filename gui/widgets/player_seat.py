"""
Displays one player's hand around the BridgeTut table.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
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

        layout.setSpacing(6)

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

        hand_container = QWidget()

        hand_container.setObjectName("handContainer")

        # IMPORTANT:
        # Transparent background.
        # This removes the big white surface.
        hand_container.setAttribute(
            Qt.WA_TranslucentBackground
        )

        position = self.player.position.value

        # -------------------------------------------------
        # NORTH / SOUTH
        # -------------------------------------------------

        if position in ("N", "S"):

            hand_layout = QHBoxLayout(hand_container)

            hand_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            # Negative spacing makes the cards overlap.
            hand_layout.setSpacing(-18)

            for card in self.player.hand.sorted_by_suit():

                card_widget = CardWidget(card)

                hand_layout.addWidget(card_widget)

            hand_layout.addStretch()

        # -------------------------------------------------
        # EAST / WEST
        # -------------------------------------------------

        else:

            hand_layout = QVBoxLayout(hand_container)

            hand_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            # Cards overlap vertically.
            hand_layout.setSpacing(-48)

            for card in self.player.hand.sorted_by_suit():

                card_widget = CardWidget(card)

                hand_layout.addWidget(card_widget)

            hand_layout.addStretch()

        layout.addWidget(hand_container)

        # -------------------------------------------------
        # SEAT STYLE
        # -------------------------------------------------

        self.setStyleSheet(self.get_style())

    def get_style(self):

        if self.active:

            return """
                QFrame#playerSeat {
                    background-color: #00582b;
                    border: 3px solid #e5c557;
                    border-radius: 10px;
                }

                QWidget#handContainer {
                    background-color: transparent;
                }
            """

        return """
            QFrame#playerSeat {
                background-color: #00582b;
                border: 1px solid transparent;
                border-radius: 10px;
            }

            QWidget#handContainer {
                background-color: transparent;
            }
        """