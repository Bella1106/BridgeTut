"""
Displays one player's hand.

PlayerSeat is responsible for:

- Displaying the player's cards.
- Highlighting the player whose turn it currently is.
- Emitting a signal when one of the player's cards is clicked.

PlayPage is responsible for deciding what happens after a card
is clicked.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
)

from .card_widget import CardWidget


class PlayerSeat(QFrame):

    # Emitted when one of this player's cards is clicked.
    card_clicked = Signal(object)

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
        self.active = active
        self.dealer = dealer
        self.hand_orientation = hand_orientation

        self.cards = []
        self.hand_widget = None
        self.card_count_label = None

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
            10,
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
            0,
        )

        header.setSpacing(6)

        position = QLabel(
            self.player.position.value
        )

        position.setObjectName(
            "playerPosition"
        )

        header.addWidget(position)

        if self.role:

            role_label = QLabel(
                self.role.upper()
            )

            role_label.setObjectName(
                "playerRole"
            )

            header.addWidget(role_label)

        header.addStretch()

        self.card_count_label = QLabel(
            f"{len(self.player.hand)} CARDS"
        )

        self.card_count_label.setObjectName(
            "cardCount"
        )

        header.addWidget(
            self.card_count_label
        )

        self.main_layout.addLayout(header)

        # -------------------------------------------------
        # CREATE HAND
        # -------------------------------------------------

        self.rebuild_hand()

        self.update_style()

    # =====================================================
    # REBUILD HAND
    # =====================================================

    def rebuild_hand(self):

        # Remove the previous hand widget.
        if self.hand_widget is not None:

            self.main_layout.removeWidget(
                self.hand_widget
            )

            self.hand_widget.deleteLater()

            self.hand_widget = None

        # Update card count.
        if self.card_count_label is not None:

            self.card_count_label.setText(
                f"{len(self.player.hand)} CARDS"
            )

        # -------------------------------------------------
        # CREATE CARD WIDGETS
        # -------------------------------------------------

        self.cards = []

        for card in self.player.hand.sorted_by_suit():

            card_widget = CardWidget(card)

            # Make sure the widget knows its card.
            card_widget.card = card

            # Send the clicked card to PlayPage.
            card_widget.clicked.connect(
                lambda checked=False,
                       c=card:
                    self.card_clicked.emit(c)
            )

            # Only the active player's cards can be clicked.
            card_widget.setEnabled(
                self.active
            )

            self.cards.append(
                card_widget
            )

        # -------------------------------------------------
        # CREATE HAND LAYOUT
        # -------------------------------------------------

        self.update_hand_layout()

    # =====================================================
    # RESPONSIVE HAND
    # =====================================================

    def update_hand_layout(self):

        if self.hand_widget is not None:

            self.main_layout.removeWidget(
                self.hand_widget
            )

            self.hand_widget.deleteLater()

            self.hand_widget = None

        if self.hand_orientation == "vertical":

            self.hand_widget = (
                self.create_vertical_hand()
            )

        else:

            self.hand_widget = (
                self.create_horizontal_hand()
            )

        self.main_layout.addWidget(
            self.hand_widget,
            alignment=Qt.AlignCenter,
        )

    # =====================================================
    # HORIZONTAL HAND
    # =====================================================

    def create_horizontal_hand(self):

        card_width = 42
        card_height = 68

        number_of_cards = len(self.cards)

        available_width = self.width() - 24

        if available_width <= 0:
            available_width = 680

        normal_width = (
            number_of_cards * card_width
            + max(0, number_of_cards - 1) * 2
        )

        # -------------------------------------------------
        # EMPTY HAND
        # -------------------------------------------------

        if number_of_cards == 0:

            hand_widget = QWidget()

            hand_widget.setFixedSize(
                card_width,
                card_height,
            )

            hand_widget.setStyleSheet(
                "background: transparent;"
            )

            return hand_widget

        # -------------------------------------------------
        # NORMAL MODE
        # -------------------------------------------------

        if normal_width <= available_width:

            hand_widget = QWidget()

            hand_widget.setFixedHeight(
                card_height
            )

            hand_widget.setMinimumWidth(
                normal_width
            )

            hand_widget.setStyleSheet(
                "background: transparent;"
            )

            hand_layout = QHBoxLayout(
                hand_widget
            )

            hand_layout.setContentsMargins(
                0,
                0,
                0,
                0,
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
        # COMPACT MODE
        # -------------------------------------------------

        if number_of_cards > 1:

            overlap_step = (
                available_width - card_width
            ) / (number_of_cards - 1)

            overlap_step = max(
                22,
                int(overlap_step),
            )

        else:

            overlap_step = card_width

        total_width = (
            card_width
            + (number_of_cards - 1)
            * overlap_step
        )

        total_width = min(
            int(total_width),
            int(available_width),
        )

        hand_widget = QWidget()

        hand_widget.setFixedSize(
            total_width,
            card_height,
        )

        hand_widget.setStyleSheet(
            "background: transparent;"
        )

        for index, card_widget in enumerate(
            self.cards
        ):

            card_widget.setParent(
                hand_widget
            )

            x = index * overlap_step

            card_widget.move(
                int(x),
                0,
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
            total_height,
        )

        hand_widget.setStyleSheet(
            "background: transparent;"
        )

        for index, card_widget in enumerate(
            self.cards
        ):

            card_widget.setParent(
                hand_widget
            )

            card_widget.move(
                0,
                index * overlap_step,
            )

            card_widget.show()

        return hand_widget

    # =====================================================
    # ACTIVE PLAYER
    # =====================================================

    def set_active(self, active):

        self.active = active

        # Enable/disable this player's cards.
        for card_widget in self.cards:

            card_widget.setEnabled(
                active
            )

        self.update_style()

    # =====================================================
    # RESPONSIVE RESIZE
    # =====================================================

    def resizeEvent(self, event):

        super().resizeEvent(event)

        if self.hand_orientation == "horizontal":

            self.update_hand_layout()

    # =====================================================
    # STYLE
    # =====================================================

    def update_style(self):

        if self.active:

            self.setStyleSheet("""
                QFrame#playerSeat {
                    background-color: #00582b;
                    border: 3px solid #e5c557;
                    border-radius: 10px;
                }

                QLabel#playerPosition {
                    color: #e5c557;
                    font-size: 14px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }

                QLabel#playerRole {
                    color: #e5c557;
                    font-size: 12px;
                    font-weight: bold;
                    letter-spacing: 1px;
                    background: transparent;
                    border: none;
                }

                QLabel#cardCount {
                    color: #aebbb5;
                    font-size: 12px;
                    background: transparent;
                    border: none;
                }
            """)

        else:

            self.setStyleSheet("""
                QFrame#playerSeat {
                    background-color: #00582b;
                    border: 1px solid transparent;
                    border-radius: 10px;
                }

                QLabel#playerPosition {
                    color: #e5c557;
                    font-size: 14px;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }

                QLabel#playerRole {
                    color: #e5c557;
                    font-size: 12px;
                    font-weight: bold;
                    letter-spacing: 1px;
                    background: transparent;
                    border: none;
                }

                QLabel#cardCount {
                    color: #aebbb5;
                    font-size: 12px;
                    background: transparent;
                    border: none;
                }
            """)