"""
Bidding screen for BridgeTut.

The GUI integrates with the existing BiddingSystem.

The GUI does NOT implement bidding rules itself.
It creates Bid objects and passes them to:
    BiddingSystem.make_bid()
    BiddingSystem.make_pass()
    BiddingSystem.make_double()
    BiddingSystem.make_redouble()

When the auction finishes, the existing contract/declarer
logic is used to determine the Contract.

The GUI then passes the completed game data to PlayPage.

The game is NOT saved to HistoryManager here.
The game is saved by PlayPage.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from bidding.bid import Bid, Denomination
from bidding.bidding_system import (
    BiddingSystem,
    SpecialCall,
)
from card_model.deck import new_deal, deal_from
from card_model.player import Position
from contract.contract import determine_contract
from game_logic.vulnerability import determine_vulnerability
from game_logic.guided_bidding import GuidedBiddingState

from .widgets.player_seat import PlayerSeat

# =========================================================
# DISPLAY-ONLY DENOMINATION HELPERS
# =========================================================

DENOM_SYMBOL = {
    Denomination.CLUBS: "♣",
    Denomination.DIAMONDS: "♦",
    Denomination.HEARTS: "♥",
    Denomination.SPADES: "♠",
    Denomination.NO_TRUMP: "NT",
}

DENOM_IS_RED = {
    Denomination.CLUBS: False,
    Denomination.DIAMONDS: True,
    Denomination.HEARTS: True,
    Denomination.SPADES: False,
    Denomination.NO_TRUMP: False,
}

RED_SUIT_COLOR = "#c0392b"
BLACK_SUIT_COLOR = "#1a1a1a"

# Stands in for "black" wherever the background is dark.
BLACK_SUIT_COLOR_ON_DARK = "#dfe3e0"

POSITIONS_IN_ORDER = [
    Position.NORTH,
    Position.EAST,
    Position.SOUTH,
    Position.WEST,
]


class BiddingPage(QWidget):

    def __init__(
        self,
        dealer=Position.SOUTH,
        board_number=1,
        guided_bidding_state: GuidedBiddingState | None = None,
        tutorial_lesson_data=None,
        parent=None,
    ):
        super().__init__(parent)

        # =================================================
        # GUIDED BIDDING / MODE 1
        # =================================================
        self.guided_bidding_state = guided_bidding_state
        self.tutorial_lesson_data = tutorial_lesson_data

        # =================================================
        # DEALER
        # =================================================
        if self.tutorial_lesson_data is not None:
            self.dealer = (
                self.tutorial_lesson_data.dealer
            )
        else:
            self.dealer = dealer

        # =================================================
        # BOARD
        # =================================================

        self.board_number = board_number

        if self.tutorial_lesson_data is not None:
            self.vulnerability = (
                self.tutorial_lesson_data.vulnerability
            )
        else:
            self.vulnerability = determine_vulnerability(
                board_number
            )

        # =================================================
        # DEAL
        # =================================================
        if self.tutorial_lesson_data is not None:
            self.players = deal_from(
                self.tutorial_lesson_data.hands
            )
        else:
            self.players = new_deal(
                dealer=self.dealer,
            )

        # =================================================
        # BIDDING SYSTEM
        # =================================================
        if self.guided_bidding_state is not None:
            self.bidding_system = (
                self.guided_bidding_state.bidding_system
            )
        else:
            self.bidding_system = BiddingSystem(
                self.dealer
            )

        # =================================================
        # UI REFERENCES
        # =================================================

        self.bid_buttons = []

        self.pass_button = None

        self.double_button = None

        self.redouble_button = None

        self.info_values = {}

        self.auction_layout = None

        self.auction_empty = None

        self.player_seats = {}

        self.auction_circle = None

        self.auction_bid_label = None

        self.auction_by_label = None

        self.auction_status_label = None

        # Prevent finishing the auction twice.
        self.auction_completed = False

        # =================================================
        # BUILD UI
        # =================================================

        self.setup_ui()

        if self.guided_bidding_state is not None:
            self.advance_guided_bidding()

        self.update_bidding_ui()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        main_layout.setSpacing(
            16
        )

        # =================================================
        # LEFT: TABLE
        # =================================================

        table = QFrame()

        table.setObjectName(
            "biddingTable"
        )

        table_layout = QGridLayout(
            table
        )

        table_layout.setContentsMargins(
            14,
            14,
            14,
            14,
        )

        table_layout.setHorizontalSpacing(
            18
        )

        table_layout.setVerticalSpacing(
            18
        )

        # =================================================
        # PLAYER SEATS
        # =================================================

        north = PlayerSeat(
            self.players[Position.NORTH],
            role=(
                "Dealer"
                if self.dealer == Position.NORTH
                else ""
            ),
            active=False,
            dealer=(
                self.dealer == Position.NORTH
            ),
            hand_orientation="horizontal",
        )

        south = PlayerSeat(
            self.players[Position.SOUTH],
            role=(
                "Dealer"
                if self.dealer == Position.SOUTH
                else ""
            ),
            active=False,
            dealer=(
                self.dealer == Position.SOUTH
            ),
            hand_orientation="horizontal",
        )

        west = PlayerSeat(
            self.players[Position.WEST],
            role=(
                "Dealer"
                if self.dealer == Position.WEST
                else ""
            ),
            active=False,
            dealer=(
                self.dealer == Position.WEST
            ),
            hand_orientation="vertical",
        )

        east = PlayerSeat(
            self.players[Position.EAST],
            role=(
                "Dealer"
                if self.dealer == Position.EAST
                else ""
            ),
            active=False,
            dealer=(
                self.dealer == Position.EAST
            ),
            hand_orientation="vertical",
        )

        self.player_seats = {
            Position.NORTH: north,
            Position.EAST: east,
            Position.SOUTH: south,
            Position.WEST: west,
        }

        # =================================================
        # CENTRE AUCTION DISPLAY
        # =================================================

        self.auction_circle = (
            self.build_auction_circle()
        )

        # =================================================
        # TABLE POSITIONS
        # =================================================

        table_layout.addWidget(
            north,
            0,
            0,
            1,
            3,
            alignment=(
                Qt.AlignHCenter
                | Qt.AlignTop
            ),
        )

        table_layout.addWidget(
            west,
            1,
            0,
            alignment=(
                Qt.AlignVCenter
                | Qt.AlignLeft
            ),
        )

        table_layout.addWidget(
            self.auction_circle,
            1,
            1,
            alignment=Qt.AlignCenter,
        )

        table_layout.addWidget(
            east,
            1,
            2,
            alignment=(
                Qt.AlignVCenter
                | Qt.AlignRight
            ),
        )

        table_layout.addWidget(
            south,
            2,
            0,
            1,
            3,
            alignment=(
                Qt.AlignHCenter
                | Qt.AlignBottom
            ),
        )

        table_layout.setColumnStretch(
            0,
            1,
        )

        table_layout.setColumnStretch(
            1,
            2,
        )

        table_layout.setColumnStretch(
            2,
            1,
        )

        table_layout.setRowStretch(
            0,
            0,
        )

        table_layout.setRowStretch(
            1,
            1,
        )

        table_layout.setRowStretch(
            2,
            0,
        )

        main_layout.addWidget(
            table,
            1,
        )

        # =================================================
        # RIGHT PANEL
        # =================================================

        right_panel = QWidget()

        right_layout = QVBoxLayout(
            right_panel
        )

        right_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        right_layout.setSpacing(
            14
        )

        # =================================================
        # GAME INFO
        # =================================================

        info = QFrame()

        info.setObjectName(
            "infoPanel"
        )

        info_layout = QVBoxLayout(
            info
        )

        info_layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        self.add_info_row(
            info_layout,
            "DEALER",
            self.position_name(
                self.dealer
            ),
            "dealer",
        )

        self.add_info_row(
            info_layout,
            "VULNERABILITY",
            str(
                self.vulnerability
            ),
            "vulnerability",
        )

        self.add_info_row(
            info_layout,
            "TO CALL",
            self.position_name(
                self.bidding_system.current_player
            ),
            "to_call",
        )

        self.add_info_row(
            info_layout,
            "HIGHEST BID",
            "None",
            "highest_bid",
        )

        right_layout.addWidget(
            info
        )

        # =================================================
        # BIDDING PANEL
        # =================================================

        bidding_panel = QFrame()

        bidding_panel.setObjectName(
            "biddingPanel"
        )

        bidding_layout = QVBoxLayout(
            bidding_panel
        )

        bidding_layout.setContentsMargins(
            16,
            16,
            16,
            14,
        )

        bidding_layout.setSpacing(
            8
        )

        denominations = [
            Denomination.CLUBS,
            Denomination.DIAMONDS,
            Denomination.HEARTS,
            Denomination.SPADES,
            Denomination.NO_TRUMP,
        ]

        # =================================================
        # BID BUTTONS
        # =================================================

        for level in range(
            1,
            8,
        ):

            row = QHBoxLayout()

            row.setSpacing(
                6
            )

            level_label = QLabel(
                str(level)
            )

            level_label.setFixedWidth(
                22
            )

            level_label.setAlignment(
                Qt.AlignCenter
            )

            level_label.setObjectName(
                "levelLabel"
            )

            row.addWidget(
                level_label
            )

            for denomination in denominations:

                bid = Bid(
                    level,
                    denomination,
                )

                button = QPushButton(
                    DENOM_SYMBOL[
                        denomination
                    ]
                )

                button.setObjectName(
                    "bidButton"
                )

                button.setProperty(
                    "suit",
                    (
                        "red"
                        if DENOM_IS_RED[
                            denomination
                        ]
                        else "black"
                    ),
                )

                button.setFixedHeight(
                    36
                )

                button.setCursor(
                    Qt.PointingHandCursor
                )

                self.bid_buttons.append(
                    (
                        bid,
                        button,
                    )
                )

                button.clicked.connect(
                    lambda checked=False, selected_bid=bid:
                    self.on_bid_clicked(selected_bid)
                )

                row.addWidget(
                    button
                )

            bidding_layout.addLayout(
                row
            )

        # =================================================
        # PASS / DOUBLE / REDOUBLE
        # =================================================

        calls = QHBoxLayout()

        calls.setSpacing(
            8
        )

        # -------------------------------------------------
        # PASS
        # -------------------------------------------------

        self.pass_button = QPushButton(
            "Pass"
        )

        self.pass_button.setObjectName(
            "passButton"
        )

        self.pass_button.setCursor(
            Qt.PointingHandCursor
        )

        self.pass_button.clicked.connect(
            self.on_pass_clicked
        )

        calls.addWidget(
            self.pass_button
        )

        # -------------------------------------------------
        # DOUBLE
        # -------------------------------------------------

        self.double_button = QPushButton(
            "Double"
        )

        self.double_button.setObjectName(
            "secondaryButton"
        )

        self.double_button.setCursor(
            Qt.PointingHandCursor
        )

        self.double_button.clicked.connect(
            self.on_double_clicked
        )

        calls.addWidget(
            self.double_button
        )

        # -------------------------------------------------
        # REDOUBLE
        # -------------------------------------------------

        self.redouble_button = QPushButton(
            "Redouble"
        )

        self.redouble_button.setObjectName(
            "secondaryButton"
        )

        self.redouble_button.setCursor(
            Qt.PointingHandCursor
        )

        self.redouble_button.clicked.connect(
            self.on_redouble_clicked
        )

        calls.addWidget(
            self.redouble_button
        )

        bidding_layout.addLayout(
            calls
        )

        right_layout.addWidget(
            bidding_panel
        )

        # =================================================
        # AUCTION HISTORY
        # =================================================

        auction = QFrame()

        auction.setObjectName(
            "auctionPanel"
        )

        self.auction_layout = QVBoxLayout(
            auction
        )

        self.auction_layout.setContentsMargins(
            16,
            12,
            16,
            12,
        )

        headings = QHBoxLayout()

        for position in (
            POSITIONS_IN_ORDER
        ):

            label = QLabel(
                position.value
            )

            label.setAlignment(
                Qt.AlignCenter
            )

            label.setObjectName(
                "auctionHeading"
            )

            headings.addWidget(
                label
            )

        self.auction_layout.addLayout(
            headings
        )

        line = QFrame()

        line.setFrameShape(
            QFrame.HLine
        )

        line.setObjectName(
            "auctionLine"
        )

        self.auction_layout.addWidget(
            line
        )

        self.auction_empty = QLabel(
            "No calls yet."
        )

        self.auction_empty.setAlignment(
            Qt.AlignCenter
        )

        self.auction_empty.setObjectName(
            "auctionEmpty"
        )

        self.auction_layout.addWidget(
            self.auction_empty
        )

        right_layout.addWidget(
            auction,
            1,
        )

        main_layout.addWidget(
            right_panel,
            0,
        )

        self.setStyleSheet(
            self.get_style()
        )

    # =====================================================
    # CENTRE AUCTION CIRCLE
    # =====================================================

    def build_auction_circle(
        self,
    ):

        circle = QFrame()

        circle.setObjectName(
            "auctionCircle"
        )

        circle.setFixedSize(
            220,
            220,
        )

        layout = QGridLayout(
            circle
        )

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        layout.setHorizontalSpacing(
            2
        )

        layout.setVerticalSpacing(
            2
        )

        # -------------------------------------------------
        # COMPASS LETTERS
        # -------------------------------------------------

        north_label = QLabel(
            "N"
        )

        north_label.setObjectName(
            "compassLabel"
        )

        north_label.setAlignment(
            Qt.AlignHCenter
            | Qt.AlignTop
        )

        south_label = QLabel(
            "S"
        )

        south_label.setObjectName(
            "compassLabel"
        )

        south_label.setAlignment(
            Qt.AlignHCenter
            | Qt.AlignBottom
        )

        west_label = QLabel(
            "W"
        )

        west_label.setObjectName(
            "compassLabel"
        )

        west_label.setAlignment(
            Qt.AlignLeft
            | Qt.AlignVCenter
        )

        east_label = QLabel(
            "E"
        )

        east_label.setObjectName(
            "compassLabel"
        )

        east_label.setAlignment(
            Qt.AlignRight
            | Qt.AlignVCenter
        )

        # -------------------------------------------------
        # CENTRE CONTENT
        # -------------------------------------------------

        center = QWidget()

        center_layout = QVBoxLayout(
            center
        )

        center_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        center_layout.setSpacing(
            4
        )

        title = QLabel(
            "AUCTION"
        )

        title.setObjectName(
            "auctionTitle"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        self.auction_bid_label = QLabel(
            "—"
        )

        self.auction_bid_label.setObjectName(
            "auctionBidValue"
        )

        self.auction_bid_label.setAlignment(
            Qt.AlignCenter
        )

        self.auction_by_label = QLabel(
            ""
        )

        self.auction_by_label.setObjectName(
            "auctionByLabel"
        )

        self.auction_by_label.setAlignment(
            Qt.AlignCenter
        )

        self.auction_status_label = QLabel(
            ""
        )

        self.auction_status_label.setObjectName(
            "auctionStatusPill"
        )

        self.auction_status_label.setAlignment(
            Qt.AlignCenter
        )

        center_layout.addStretch(
            1
        )

        center_layout.addWidget(
            title
        )

        center_layout.addWidget(
            self.auction_bid_label
        )

        center_layout.addWidget(
            self.auction_by_label
        )

        center_layout.addSpacing(
            6
        )

        center_layout.addWidget(
            self.auction_status_label,
            alignment=Qt.AlignCenter,
        )

        center_layout.addStretch(
            1
        )

        # -------------------------------------------------
        # PLACE IN GRID
        # -------------------------------------------------

        layout.addWidget(
            north_label,
            0,
            0,
            1,
            3,
        )

        layout.addWidget(
            west_label,
            1,
            0,
        )

        layout.addWidget(
            center,
            1,
            1,
        )

        layout.addWidget(
            east_label,
            1,
            2,
        )

        layout.addWidget(
            south_label,
            2,
            0,
            1,
            3,
        )

        layout.setColumnStretch(
            0,
            0,
        )

        layout.setColumnStretch(
            1,
            1,
        )

        layout.setColumnStretch(
            2,
            0,
        )

        layout.setRowStretch(
            0,
            0,
        )

        layout.setRowStretch(
            1,
            1,
        )

        layout.setRowStretch(
            2,
            0,
        )

        return circle

    def update_auction_center(
        self,
    ):

        highest_bid = (
            self.bidding_system.highest_bid
        )

        if highest_bid is None:

            self.auction_bid_label.setText(
                "—"
            )

            self.auction_by_label.setText(
                ""
            )

        else:

            self.auction_bid_label.setText(
                self.bid_text(
                    highest_bid
                )
            )

            owner = (
                self.find_bid_owner(
                    highest_bid
                )
            )

            if owner is not None:

                self.auction_by_label.setText(
                    f"BY "
                    f"{self.position_name(owner).upper()}"
                )

            else:

                self.auction_by_label.setText(
                    ""
                )

        if (
            self.auction_completed
            or self.bidding_system.auction_finished
        ):

            self.auction_status_label.setText(
                "AUCTION COMPLETE"
            )

        else:

            current_player = (
                self.bidding_system.current_player
            )

            self.auction_status_label.setText(
                f"{self.position_name(current_player).upper()}"
                f" TO CALL"
            )

    def find_bid_owner(
        self,
        bid,
    ):

        for (
            position,
            entry,
        ) in reversed(
            self.bidding_system.history
        ):

            if not isinstance(
                entry,
                Bid,
            ):

                continue

            if (
                entry.level == bid.level
                and entry.denomination
                == bid.denomination
            ):

                return position

        return None

    # =====================================================
    # INFO ROW
    # =====================================================

    def add_info_row(
        self,
        layout,
        label,
        value,
        key,
    ):

        row = QHBoxLayout()

        left = QLabel(
            label
        )

        left.setObjectName(
            "infoLabel"
        )

        right = QLabel(
            value
        )

        right.setObjectName(
            "infoValue"
        )

        right.setAlignment(
            Qt.AlignRight
        )

        self.info_values[
            key
        ] = right

        row.addWidget(
            left
        )

        row.addWidget(
            right
        )

        layout.addLayout(
            row
        )

    # =====================================================
    # GUIDED BIDDING
    # =====================================================
    def advance_guided_bidding(
        self,
    ):
        if self.guided_bidding_state is None:
            return

        if self.guided_bidding_state.is_complete:
            self.finish_guided_auction()
            return

        self.guided_bidding_state.play_computer_calls()

        self.update_bidding_ui()

        if self.guided_bidding_state.is_complete:
            self.finish_guided_auction()

    # =====================================================
    # BID CLICK
    # =====================================================

    def on_bid_clicked(
        self,
        bid,
    ):

        if self.auction_completed:

            return

        if self.guided_bidding_state is not None:
            accepted = (
                self.guided_bidding_state.attempt_call(
                    bid
                )
            )

            if not accepted:
                return

            self.advance_guided_bidding()
            return

        player = (
            self.bidding_system.current_player
        )

        accepted = (
            self.bidding_system.make_bid(
                player,
                bid,
            )
        )

        if not accepted:

            return

        self.update_bidding_ui()

        self.check_auction_finished()

    # =====================================================
    # PASS CLICK
    # =====================================================

    def on_pass_clicked(
        self,
    ):

        if self.auction_completed:

            return

        if self.guided_bidding_state is not None:
            accepted = (
                self.guided_bidding_state.attempt_call(
                    None
                )
            )

            if not accepted:
                return

            self.advance_guided_bidding()
            return

        player = (
            self.bidding_system.current_player
        )

        accepted = (
            self.bidding_system.make_pass(
                player
            )
        )

        if not accepted:

            return

        self.update_bidding_ui()

        self.check_auction_finished()

    # =====================================================
    # DOUBLE CLICK
    # =====================================================

    def on_double_clicked(
        self,
    ):

        if self.auction_completed:

            return

        if self.guided_bidding_state is not None:
            accepted = (
                self.guided_bidding_state.attempt_call(
                    SpecialCall.DOUBLE
                )
            )

            if not accepted:
                return

            self.advance_guided_bidding()
            return

        player = (
            self.bidding_system.current_player
        )

        accepted = (
            self.bidding_system.make_double(
                player
            )
        )

        if not accepted:

            return

        self.update_bidding_ui()

        self.check_auction_finished()

    # =====================================================
    # REDOUBLE CLICK
    # =====================================================

    def on_redouble_clicked(
        self,
    ):

        if self.auction_completed:

            return

        if self.guided_bidding_state is not None:
            accepted = (
                self.guided_bidding_state.attempt_call(
                    SpecialCall.REDOUBLE
                )
            )

            if not accepted:
                return

            self.advance_guided_bidding()
            return

        player = (
            self.bidding_system.current_player
        )

        accepted = (
            self.bidding_system.make_redouble(
                player
            )
        )

        if not accepted:

            return

        self.update_bidding_ui()

        self.check_auction_finished()

    # =====================================================
    # UPDATE UI
    # =====================================================

    def update_bidding_ui(
        self,
    ):

        current_player = (
            self.bidding_system.current_player
        )

        highest_bid = (
            self.bidding_system.highest_bid
        )

        if self.guided_bidding_state is not None:
            user_can_call = (
                self.guided_bidding_state.is_user_turn
                and not self.guided_bidding_state.is_complete
            )
        else:
            user_can_call = True

        self.info_values[
            "to_call"
        ].setText(
            self.position_name(
                current_player
            )
        )

        if highest_bid is None:

            highest_text = "None"

        else:

            owner = (
                self.find_bid_owner(
                    highest_bid
                )
            )

            owner_text = (
                f" by {owner.value}"
                if owner is not None
                else ""
            )

            highest_text = (
                self.bid_html_dark(
                    highest_bid
                )
                + owner_text
            )

        self.info_values[
            "highest_bid"
        ].setText(
            highest_text
        )

        # =================================================
        # NORMAL BID BUTTONS
        # =================================================

        for (
            bid,
            button,
        ) in self.bid_buttons:

            legal = (
                self.bidding_system.is_valid_bid(
                    bid
                )
            )

            button.setEnabled(
                legal
                and user_can_call
                and not self.bidding_system.auction_finished
                and not self.auction_completed
            )

        # =================================================
        # PASS
        # =================================================

        self.pass_button.setEnabled(
            user_can_call
            and not self.bidding_system.auction_finished
            and not self.auction_completed
        )

        # =================================================
        # DOUBLE
        # =================================================

        self.double_button.setEnabled(
            user_can_call
            and self.bidding_system.can_double(
                current_player
            )
        )

        # =================================================
        # REDOUBLE
        # =================================================

        self.redouble_button.setEnabled(
            user_can_call
            and 
            self.bidding_system.can_redouble(
                current_player
            )
        )

        # =================================================
        # REFRESH
        # =================================================

        self.update_auction_history()

        self.update_active_player()

        self.update_auction_center()

    # =====================================================
    # ACTIVE PLAYER
    # =====================================================

    def update_active_player(
        self,
    ):

        current_player = (
            self.bidding_system.current_player
        )

        for (
            position,
            seat,
        ) in self.player_seats.items():

            is_current = (
                position == current_player
                and not self.auction_completed
            )

            seat.set_active(
                is_current
            )

            seat.setProperty(
                "biddingActive",
                is_current,
            )

            seat.style().unpolish(
                seat
            )

            seat.style().polish(
                seat
            )

            seat.update()

    # =====================================================
    # AUCTION HISTORY
    # =====================================================

    def update_auction_history(
        self,
    ):

        while (
            self.auction_layout.count()
            > 2
        ):

            item = (
                self.auction_layout.takeAt(
                    2
                )
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

        history = (
            self.bidding_system.history
        )

        if not history:

            empty = QLabel(
                "No calls yet."
            )

            empty.setAlignment(
                Qt.AlignCenter
            )

            empty.setObjectName(
                "auctionEmpty"
            )

            self.auction_layout.addWidget(
                empty
            )

            return

        for auction_row in (
            self.build_auction_rows(
                history
            )
        ):

            row_widget = QWidget()

            row_layout = QHBoxLayout(
                row_widget
            )

            row_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            row_layout.setSpacing(
                4
            )

            for position in (
                POSITIONS_IN_ORDER
            ):

                label = QLabel(
                    auction_row[position]
                )

                label.setAlignment(
                    Qt.AlignCenter
                )

                label.setObjectName(
                    "auctionCall"
                )

                row_layout.addWidget(
                    label
                )

            self.auction_layout.addWidget(
                row_widget
            )

    def build_auction_rows(
        self,
        history,
    ):

        rows = []

        current_row = {
            position: ""
            for position in POSITIONS_IN_ORDER
        }

        row_started = False

        for (
            position,
            call,
        ) in history:

            # -------------------------------------------------
            # NORTH STARTING A NEW ROW
            # -------------------------------------------------

            if (
                position == Position.NORTH
                and row_started
            ):

                rows.append(
                    current_row
                )

                current_row = {
                    position: ""
                    for position
                    in POSITIONS_IN_ORDER
                }

                row_started = False

            # -------------------------------------------------
            # DISPLAY CALL
            # -------------------------------------------------

            if call is None:

                display_call = "Pass"

            elif isinstance(
                call,
                Bid,
            ):

                display_call = (
                    self.bid_html_dark(
                        call
                    )
                )

            elif call == SpecialCall.DOUBLE:

                display_call = "Double"

            elif call == SpecialCall.REDOUBLE:

                display_call = "Redouble"

            else:

                display_call = str(
                    call
                )

            current_row[
                position
            ] = display_call

            row_started = True

        if row_started:

            rows.append(
                current_row
            )

        return rows

    # =====================================================
    # CHECK AUCTION FINISHED
    # =====================================================

    def check_auction_finished(
        self,
    ):

        if self.auction_completed:

            return

        if self.bidding_system.auction_finished:

            self.finish_auction()

    # =====================================================
    # FINISH AUCTION
    # =====================================================

    def finish_auction(
        self,
    ):

        if self.auction_completed:

            return

        self.auction_completed = True

        contract = (
            determine_contract(
                self.bidding_system
            )
        )

        declarer = None

        if contract is not None:

            declarer = contract.declarer

        window = self.window()

        if hasattr(
            window,
            "play_data",
        ):

            window.play_data = {
                "players": self.players,
                "dealer": self.dealer,
                "board_number": self.board_number,
                "contract": contract,
                "declarer": declarer,

                # Preserve the full auction history,
                # including Double and Redouble.

                "history": list(
                    self.bidding_system.history
                ),

                # Preserve the final doubling state.

                "doubling_state": (
                    self.bidding_system.doubling_state
                ),
            }

        self.update_bidding_ui()

        if hasattr(
            window,
            "navigate",
        ):

            window.navigate(
                "Play"
            )

    # =====================================================
    # DISPLAY HELPERS
    # =====================================================

    @staticmethod
    def position_name(
        position,
    ):

        if position is None:

            return "—"

        return {
            Position.NORTH: "North",
            Position.EAST: "East",
            Position.SOUTH: "South",
            Position.WEST: "West",
        }[position]

    @staticmethod
    def bid_text(
        bid,
    ):

        return (
            f"{bid.level}"
            f"{DENOM_SYMBOL[bid.denomination]}"
        )

    @staticmethod
    def bid_html(
        bid,
    ):

        symbol = (
            DENOM_SYMBOL[
                bid.denomination
            ]
        )

        color = (
            RED_SUIT_COLOR
            if DENOM_IS_RED[
                bid.denomination
            ]
            else BLACK_SUIT_COLOR
        )

        return (
            f'{bid.level}'
            f'<span style="color:{color};">'
            f'{symbol}'
            f'</span>'
        )

    @staticmethod
    def bid_html_dark(
        bid,
    ):

        symbol = (
            DENOM_SYMBOL[
                bid.denomination
            ]
        )

        color = (
            RED_SUIT_COLOR
            if DENOM_IS_RED[
                bid.denomination
            ]
            else BLACK_SUIT_COLOR_ON_DARK
        )

        return (
            f'{bid.level}'
            f'<span style="color:{color};">'
            f'{symbol}'
            f'</span>'
        )

    # =====================================================
    # STYLE
    # =====================================================

    def get_style(
        self,
    ):

        return """

        QWidget {
            font-family: "Segoe UI", Arial, sans-serif;
        }

        QFrame#biddingTable {
            background-color: #00602e;
            border-radius: 12px;
        }

        QFrame#playerSeat {
            background-color: #00582b;
            border-radius: 10px;
        }

        QFrame#playerSeat[biddingActive="true"] {
            border: 3px solid #e5c557;
            border-radius: 10px;
        }

        QFrame#playerSeat[biddingActive="false"] {
            border: 1px solid transparent;
            border-radius: 10px;
        }

        QFrame#auctionCircle {
            background-color: #0b4a26;
            border: 2px solid #1d6e3f;
            border-radius: 110px;
        }

        QLabel#compassLabel {
            color: #e5c557;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        QLabel#auctionTitle {
            color: #b9c8c1;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        QLabel#auctionBidValue {
            color: #e5c557;
            font-size: 30px;
            font-weight: bold;
        }

        QLabel#auctionByLabel {
            color: #e5c557;
            font-size: 12px;
            letter-spacing: 1px;
        }

        QLabel#auctionStatusPill {
            background-color: rgba(229, 197, 87, 40);
            color: #f1f4f2;
            border: 1px solid rgba(229, 197, 87, 90);
            border-radius: 12px;
            padding: 6px 10px;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        QFrame#infoPanel,
        QFrame#biddingPanel,
        QFrame#auctionPanel {
            background-color: #11271d;
            border: 1px solid #29483b;
            border-radius: 10px;
        }

        QLabel {
            color: #f1f4f2;
        }

        QLabel#infoLabel {
            color: #b9c8c1;
            font-size: 12px;
            letter-spacing: 1px;
        }

        QLabel#infoValue {
            color: white;
            font-size: 13px;
            font-weight: bold;
        }

        QLabel#levelLabel {
            color: #d0d9d4;
            font-size: 13px;
        }

        QPushButton#bidButton {
            background-color: #fffef7;
            color: #1a1a1a;
            border: none;
            border-radius: 5px;
            font-size: 15px;
            font-weight: bold;
        }

        QPushButton#bidButton[suit="red"] {
            color: #c0392b;
        }

        QPushButton#bidButton[suit="black"] {
            color: #1a1a1a;
        }

        QPushButton#bidButton:hover {
            background-color: #e5c557;
        }

        QPushButton#bidButton:disabled {
            background-color: #3c4742;
            color: #737c77;
        }

        QPushButton#passButton {
            background-color: #51b5ba;
            color: #071710;
            border: none;
            border-radius: 6px;
            padding: 9px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton#passButton:hover {
            background-color: #6bc8cc;
        }

        QPushButton#passButton:disabled {
            background-color: #3c4742;
            color: #737c77;
        }

        QPushButton#secondaryButton {
            background-color: #11271d;
            color: white;
            border: 1px solid #29483b;
            border-radius: 6px;
            padding: 9px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton#secondaryButton:hover {
            background-color: #173629;
        }

        QPushButton#secondaryButton:disabled {
            background-color: #11271d;
            color: #59645f;
            border: 1px solid #26342e;
        }

        QLabel#auctionHeading {
            color: #b9c8c1;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        QFrame#auctionLine {
            color: #29483b;
            background-color: #29483b;
            max-height: 1px;
        }

        QLabel#auctionEmpty {
            color: #b9c8c1;
            padding: 10px;
        }

        QLabel#auctionCall {
            color: #f1f4f2;
            font-size: 13px;
            font-weight: bold;
            padding: 4px;
        }

        """