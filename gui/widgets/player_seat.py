"""
Displays one player's hand.
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
    """
    Displays one player's hand.

    Normal size:
        Cards are displayed next to each other.

    Smaller window:
        Cards automatically overlap so all 13 cards
        continue to fit inside the player area.

    Dealer:
        The player who is the dealer receives the
        gold border around their entire player block.
    """

    def __init__(
        self,
        player,
        role="",
        active=False,
        dealer=False,
        hand_orientation="horizontal",
        parent=None,
    ):
        super().__init__(parent)

        self.player = player
        self.role = role

        # Kept for game logic / future use.
        # It no longer controls the gold border.
        self.active = active

        # Only this controls the gold border.
        self.dealer = dealer

        self.hand_orientation = hand_orientation

        self.cards = []
        self.hand_widget = None

        self.setup_ui()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        self.setObjectName("playerSeat")

        self.main_layout = QVBoxLayout(self)

        self.main_layout.setContentsMargins(
            12,
            10,
            12,
            10
        )

        self.main_layout.setSpacing(6)

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = QHBoxLayout()

        header.setContentsMargins(
            0,
            0,
            0,
            0
        )

        header.setSpacing(6)

        # Player position
        position = QLabel(
            self.player.position.value
        )

        position.setStyleSheet("""
            color: #e5c557;
            font-size: 14px;
            font-weight: bold;
        """)

        header.addWidget(position)

        # Player role
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

        # Number of cards
        card_count = QLabel(
            f"{len(self.player.hand)} CARDS"
        )

        card_count.setStyleSheet("""
            color: #aebbb5;
            font-size: 12px;
        """)

        header.addWidget(card_count)

        self.main_layout.addLayout(header)

        # -------------------------------------------------
        # CREATE CARDS
        # -------------------------------------------------

        self.cards = [
            CardWidget(card)
            for card in self.player.hand.sorted_by_suit()
        ]

        # Create initial hand
        self.update_hand_layout()

        # Apply player-seat styling
        self.setStyleSheet(self.get_style())

    # =====================================================
    # RESPONSIVE HAND
    # =====================================================

    def update_hand_layout(self):

        # Remove the old hand widget
        if self.hand_widget is not None:

            self.main_layout.removeWidget(
                self.hand_widget
            )

            self.hand_widget.deleteLater()

            self.hand_widget = None

        # -------------------------------------------------
        # VERTICAL HAND
        # -------------------------------------------------

        if self.hand_orientation == "vertical":

            self.hand_widget = self.create_vertical_hand()

        # -------------------------------------------------
        # HORIZONTAL HAND
        # -------------------------------------------------

        else:

            self.hand_widget = self.create_horizontal_hand()

        self.main_layout.addWidget(
            self.hand_widget,
            alignment=Qt.AlignCenter
        )

    # =====================================================
    # HORIZONTAL HAND
    # =====================================================

    def create_horizontal_hand(self):

        card_width = 42
        card_height = 68

        number_of_cards = len(self.cards)

        # Width available inside PlayerSeat.
        available_width = self.width() - 24

        # During initial construction the widget may not
        # have its final width yet.
        if available_width <= 0:
            available_width = 680

        # -------------------------------------------------
        # NORMAL MODE
        # -------------------------------------------------
        #
        # If all cards fit normally, keep them completely
        # separated.
        #

        normal_width = (
            number_of_cards * card_width
            + max(0, number_of_cards - 1) * 2
        )

        if normal_width <= available_width:

            hand_widget = QWidget()

            hand_widget.setFixedHeight(
                card_height
            )

            hand_widget.setMinimumWidth(
                normal_width
            )

            hand_widget.setStyleSheet("""
                background: transparent;
            """)

            hand_layout = QHBoxLayout(
                hand_widget
            )

            hand_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            hand_layout.setSpacing(2)

            for card_widget in self.cards:

                card_widget.setParent(
                    hand_widget
                )

                hand_layout.addWidget(
                    card_widget
                )

            return hand_widget

        # -------------------------------------------------
        # STACKED / COMPACT MODE
        # -------------------------------------------------
        #
        # Only activate this when the cards no longer
        # fit side-by-side.
        #

        if number_of_cards > 1:

            overlap_step = (
                available_width - card_width
            ) / (number_of_cards - 1)

            # Keep enough of each card visible.
            overlap_step = max(
                22,
                int(overlap_step)
            )

        else:

            overlap_step = card_width

        total_width = (
            card_width
            + (number_of_cards - 1) * overlap_step
        )

        # Never allow the hand widget to become wider
        # than the available player-seat area.
        total_width = min(
            int(total_width),
            int(available_width)
        )

        hand_widget = QWidget()

        hand_widget.setFixedSize(
            total_width,
            card_height
        )

        hand_widget.setStyleSheet("""
            background: transparent;
        """)

        # -------------------------------------------------
        # MANUAL CARD POSITIONING
        # -------------------------------------------------

        for index, card_widget in enumerate(
            self.cards
        ):

            card_widget.setParent(
                hand_widget
            )

            x = index * overlap_step

            card_widget.move(
                int(x),
                0
            )

            card_widget.show()

        return hand_widget

    # =====================================================
    # VERTICAL HAND
    # =====================================================

    def create_vertical_hand(self):

        card_width = 42
        card_height = 68

        number_of_cards = len(self.cards)

        # Cards overlap vertically.
        overlap_step = 22

        if number_of_cards > 0:

            total_height = (
                card_height
                + (number_of_cards - 1)
                * overlap_step
            )

        else:

            total_height = card_height

        hand_widget = QWidget()

        hand_widget.setFixedSize(
            card_width,
            total_height
        )

        hand_widget.setStyleSheet("""
            background: transparent;
        """)

        # -------------------------------------------------
        # MANUAL CARD POSITIONING
        # -------------------------------------------------

        for index, card_widget in enumerate(
            self.cards
        ):

            card_widget.setParent(
                hand_widget
            )

            x = 0
            y = index * overlap_step

            card_widget.move(
                x,
                y
            )

            card_widget.show()

        return hand_widget

    # =====================================================
    # RESPONSIVE RESIZE
    # =====================================================

    def resizeEvent(self, event):

        super().resizeEvent(event)

        # Only horizontal hands need to switch between
        # normal and compact modes.
        if self.hand_orientation == "horizontal":

            self.update_hand_layout()

    # =====================================================
    # STYLE
    # =====================================================

    def get_style(self):

        # -------------------------------------------------
        # DEALER
        # -------------------------------------------------
        #
        # ONLY the dealer receives the gold border.
        #

        if self.dealer:

            return """
                QFrame#playerSeat {
                    background-color: #00582b;
                    border: 3px solid #e5c557;
                    border-radius: 10px;
                }
            """

        # -------------------------------------------------
        # NORMAL PLAYER
        # -------------------------------------------------

        return """
            QFrame#playerSeat {
                background-color: #00582b;
                border: 1px solid transparent;
                border-radius: 10px;
            }
        """