"""
Bidding screen for BridgeTut.

The GUI integrates with the existing BiddingSystem from the
team's bidding package.

The GUI does NOT implement bidding rules itself. It creates Bid
objects and passes them to BiddingSystem.make_bid() / make_pass().
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
from bidding.bidding_system import BiddingSystem

from card_model.deck import new_deal
from card_model.player import Position

from .widgets.player_seat import PlayerSeat


class BiddingPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # =================================================
        # TEMPORARY DEALER
        # =================================================
        #
        # Dealer system has not been implemented yet.
        # For now, South is always the dealer.
        #

        self.dealer = Position.SOUTH

        # =================================================
        # DEAL
        # =================================================

        self.players = new_deal(
            dealer=self.dealer,
            seed=42,
        )

        # =================================================
        # BIDDING SYSTEM
        # =================================================

        # IMPORTANT:
        # We are using the team's existing BiddingSystem.
        #
        self.bidding_system = BiddingSystem(
            self.dealer
        )

        # =================================================
        # UI REFERENCES
        # =================================================

        self.bid_buttons = []

        self.pass_button = None

        self.info_values = {}

        self.auction_empty = None

        self.auction_layout = None

        self.setup_ui()

        # Update UI to reflect the initial state
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
            16
        )

        main_layout.setSpacing(16)

        # =================================================
        # LEFT TABLE
        # =================================================

        table = QFrame()

        table.setObjectName(
            "biddingTable"
        )

        table_layout = QGridLayout(table)

        table_layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        table_layout.setSpacing(10)

        # -------------------------------------------------
        # SEATS
        # -------------------------------------------------

        self.player_seats = {}

        north = PlayerSeat(
            self.players[Position.NORTH],
            role="",
            active=(self.bidding_system.current_player == Position.NORTH),
            dealer=(self.dealer == Position.NORTH),
            hand_orientation="horizontal",
        )

        east = PlayerSeat(
            self.players[Position.EAST],
            role="",
            active=(self.bidding_system.current_player == Position.EAST),
            dealer=(self.dealer == Position.EAST),
            hand_orientation="horizontal",
        )

        south = PlayerSeat(
            self.players[Position.SOUTH],
            role="Dealer",
            active=(self.bidding_system.current_player == Position.SOUTH),
            dealer=(self.dealer == Position.SOUTH),
            hand_orientation="horizontal",
        )

        west = PlayerSeat(
            self.players[Position.WEST],
            role="",
            active=(self.bidding_system.current_player == Position.WEST),
            dealer=(self.dealer == Position.WEST),
            hand_orientation="horizontal",
        )

        self.player_seats = {
            Position.NORTH: north,
            Position.EAST: east,
            Position.SOUTH: south,
            Position.WEST: west,
        }

        # -------------------------------------------------
        # TABLE POSITIONS
        # -------------------------------------------------

        # North = top left
        table_layout.addWidget(
            north,
            0,
            0
        )

        # East = top right
        table_layout.addWidget(
            east,
            0,
            1
        )

        # South = bottom right
        table_layout.addWidget(
            south,
            1,
            1
        )

        # West = bottom left
        table_layout.addWidget(
            west,
            1,
            0
        )

        table_layout.setColumnStretch(
            0,
            1
        )

        table_layout.setColumnStretch(
            1,
            1
        )

        table_layout.setRowStretch(
            0,
            1
        )

        table_layout.setRowStretch(
            1,
            1
        )

        main_layout.addWidget(
            table,
            1
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
            0
        )

        right_layout.setSpacing(14)

        # =================================================
        # CONTRACT INFO
        # =================================================

        info = QFrame()

        info.setObjectName(
            "infoPanel"
        )

        info_layout = QVBoxLayout(info)

        info_layout.setContentsMargins(
            16,
            14,
            16,
            14
        )

        self.add_info_row(
            info_layout,
            "DEALER",
            self.position_name(
                self.dealer
            ),
            "dealer"
        )

        self.add_info_row(
            info_layout,
            "VULNERABILITY",
            "Vulnerable",
            "vulnerability"
        )

        self.add_info_row(
            info_layout,
            "TO CALL",
            self.position_name(
                self.bidding_system.current_player
            ),
            "to_call"
        )

        self.add_info_row(
            info_layout,
            "HIGHEST BID",
            "None",
            "highest_bid"
        )

        right_layout.addWidget(
            info
        )

        # =================================================
        # BIDDING GRID
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
            14
        )

        bidding_layout.setSpacing(8)

        # -------------------------------------------------
        # DENOMINATIONS
        # -------------------------------------------------

        denominations = [
            Denomination.CLUBS,
            Denomination.DIAMONDS,
            Denomination.HEARTS,
            Denomination.SPADES,
            Denomination.NO_TRUMP,
        ]

        # -------------------------------------------------
        # 1-7 BID GRID
        # -------------------------------------------------

        for level in range(1, 8):

            row = QHBoxLayout()

            row.setSpacing(6)

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
                    denomination
                )

                button = QPushButton(
                    self.bid_text(
                        bid
                    )
                )

                button.setObjectName(
                    "bidButton"
                )

                button.setFixedHeight(
                    36
                )

                button.setCursor(
                    Qt.PointingHandCursor
                )

                # Store bid/button pair.
                self.bid_buttons.append(
                    (bid, button)
                )

                # Capture the bid for the lambda.
                button.clicked.connect(
                    lambda checked=False,
                    selected_bid=bid:
                    self.on_bid_clicked(
                        selected_bid
                    )
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

        calls.setSpacing(8)

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

        double_button = QPushButton(
            "Double"
        )

        double_button.setObjectName(
            "secondaryButton"
        )

        # Not implemented by the team's BiddingSystem yet.
        double_button.setEnabled(False)

        redouble_button = QPushButton(
            "Redouble"
        )

        redouble_button.setObjectName(
            "secondaryButton"
        )

        # Not implemented by the team's BiddingSystem yet.
        redouble_button.setEnabled(False)

        calls.addWidget(
            self.pass_button
        )

        calls.addWidget(
            double_button
        )

        calls.addWidget(
            redouble_button
        )

        bidding_layout.addLayout(
            calls
        )

        right_layout.addWidget(
            bidding_panel
        )

        # =================================================
        # AUCTION
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
            12
        )

        headings = QHBoxLayout()

        # Display in table order.
        for position in [
            Position.NORTH,
            Position.EAST,
            Position.SOUTH,
            Position.WEST,
        ]:

            label = QLabel(
                position.value
            )

            label.setAlignment(
                Qt.AlignCenter
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
            auction
        )

        # =================================================
        # ADD RIGHT PANEL
        # =================================================

        main_layout.addWidget(
            right_panel,
            0
        )

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet(
            self.get_style()
        )

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

        self.info_values[key] = right

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
    # BID BUTTON CLICK
    # =====================================================

    def on_bid_clicked(
        self,
        bid,
    ):

        player = (
            self.bidding_system.current_player
        )

        # -------------------------------------------------
        # LET BIDDING SYSTEM VALIDATE IT
        # -------------------------------------------------

        accepted = (
            self.bidding_system.make_bid(
                player,
                bid
            )
        )

        if not accepted:
            return

        # -------------------------------------------------
        # UPDATE EVERYTHING
        # -------------------------------------------------

        self.update_bidding_ui()

        # -------------------------------------------------
        # CHECK WHETHER AUCTION FINISHED
        # -------------------------------------------------

        self.check_auction_finished()

    # =====================================================
    # PASS CLICK
    # =====================================================

    def on_pass_clicked(self):

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

        # -------------------------------------------------
        # UPDATE UI
        # -------------------------------------------------

        self.update_bidding_ui()

        # -------------------------------------------------
        # CHECK FINISH
        # -------------------------------------------------

        self.check_auction_finished()

    # =====================================================
    # UPDATE BIDDING UI
    # =====================================================

    def update_bidding_ui(self):

        current_player = (
            self.bidding_system.current_player
        )

        highest_bid = (
            self.bidding_system.highest_bid
        )

        # -------------------------------------------------
        # ACTIVE PLAYER / GOLD BORDER
        # -------------------------------------------------

        for position, seat in self.player_seats.items():

            seat.set_active(
                position == current_player
            )

        # -------------------------------------------------
        # TO CALL
        # -------------------------------------------------

        self.info_values[
            "to_call"
        ].setText(
            self.position_name(
                current_player
            )
        )

        # -------------------------------------------------
        # HIGHEST BID
        # -------------------------------------------------

        if highest_bid is None:

            highest_text = "None"

        else:

            highest_text = (
                self.bid_text(
                    highest_bid
                )
            )

        self.info_values[
            "highest_bid"
        ].setText(
            highest_text
        )

        # -------------------------------------------------
        # LEGAL BID BUTTONS
        # -------------------------------------------------

        for bid, button in self.bid_buttons:

            button.setEnabled(
                self.bidding_system.is_valid_bid(
                    bid
                )
                and not
                self.bidding_system.auction_finished
            )

        # -------------------------------------------------
        # PASS
        # -------------------------------------------------

        self.pass_button.setEnabled(
            not self.bidding_system.auction_finished
        )

        # -------------------------------------------------
        # AUCTION HISTORY
        # -------------------------------------------------

        self.update_auction_history()
    
    # =====================================================
    # AUCTION HISTORY
    # =====================================================

    def update_auction_history(self):

        # Remove old history widgets.
        #
        # Keep the first 2 widgets:
        #   headings
        #   horizontal line
        #

        while self.auction_layout.count() > 2:

            item = (
                self.auction_layout.takeAt(2)
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

        history = (
            self.bidding_system.history
        )

        if not history:

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

            return

        # -------------------------------------------------
        # GROUP CALLS BY AUCTION ROW
        # -------------------------------------------------
        #
        # Every four calls forms one row:
        #
        # N E S W
        #
        # The auction starts from the dealer,
        # which is South for now.
        #

        rows = []

        current_row = []

        for position, bid in history:

            current_row.append(
                (
                    position,
                    bid
                )
            )

            if len(current_row) == 4:

                rows.append(
                    current_row
                )

                current_row = []

        if current_row:

            rows.append(
                current_row
            )

        # -------------------------------------------------
        # DISPLAY ROWS
        # -------------------------------------------------

        for auction_row in rows:

            row_widget = QWidget()

            row_layout = QHBoxLayout(
                row_widget
            )

            row_layout.setContentsMargins(
                0,
                0,
                0,
                0
            )

            row_layout.setSpacing(
                4
            )

            # Four columns.
            cells = {
                Position.NORTH: "",
                Position.EAST: "",
                Position.SOUTH: "",
                Position.WEST: "",
            }

            for position, bid in auction_row:

                if bid is None:

                    text = "Pass"

                else:

                    text = self.bid_text(
                        bid
                    )

                cells[position] = text

            for position in [
                Position.NORTH,
                Position.EAST,
                Position.SOUTH,
                Position.WEST,
            ]:

                label = QLabel(
                    cells[position]
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

    # =====================================================
    # CHECK AUCTION FINISHED
    # =====================================================

    def check_auction_finished(self):

        # -------------------------------------------------
        # NORMAL FINISH
        # -------------------------------------------------
        #
        # Existing BiddingSystem sets auction_finished
        # after three passes following a bid.
        #

        if self.bidding_system.auction_finished:

            self.finish_auction()

            return

        # -------------------------------------------------
        # ALL PASS / PASSED OUT
        # -------------------------------------------------
        #
        # The existing BiddingSystem does not set
        # auction_finished for four passes when there
        # has been no bid.
        #
        # We therefore detect that condition here.
        #

        if (
            self.bidding_system.highest_bid is None
            and
            self.bidding_system.consecutive_passes >= 4
        ):

            self.finish_auction()

    # =====================================================
    # FINISH AUCTION
    # =====================================================
    def get_declarer(self):

        final_bid = self.bidding_system.highest_bid

        if final_bid is None:
            return None

        # The declarer is the first player from the declaring
        # partnership who made the final denomination bid.
        for position, bid in self.bidding_system.history:

            if bid is None:
                continue

            if (
                bid.denomination
                == final_bid.denomination
            ):

                # Same partnership as the player who made
                # the final bid.
                if (
                    position.value == self.position_partner(
                        position
                    )
                ):
                    return position

        return None
    def get_declarer(self):

        final_bid = self.bidding_system.highest_bid

        if final_bid is None:
            return None

        # Find the player who made the final bid.
        final_bidder = None

        for position, bid in self.bidding_system.history:

            if bid == final_bid:
                final_bidder = position

        if final_bidder is None:
            return None

        # Find the first player from the same partnership
        # who bid the final denomination.
        for position, bid in self.bidding_system.history:

            if bid is None:
                continue

            if bid.denomination != final_bid.denomination:
                continue

            if self.same_partnership(
                position,
                final_bidder
            ):
                return position

        return final_bidder

    def same_partnership(
        self,
        first,
        second,
    ):

        return (
            first == second
            or
            (
                first == Position.NORTH
                and second == Position.SOUTH
            )
            or
            (
                first == Position.SOUTH
                and second == Position.NORTH
            )
            or
            (
                first == Position.EAST
                and second == Position.WEST
            )
            or
            (
                first == Position.WEST
                and second == Position.EAST
            )
        )
    def finish_auction(self):

        # Prevent further input.
        self.bidding_system.auction_finished = True

        self.update_bidding_ui()

        # -------------------------------------------------
        # DETERMINE FINAL CONTRACT
        # -------------------------------------------------

        final_bid = self.bidding_system.highest_bid

        declarer = self.get_declarer()

        # -------------------------------------------------
        # STORE GAME DATA ON MAIN WINDOW
        # -------------------------------------------------

        window = self.window()

        window.play_data = {
            "players": self.players,
            "dealer": self.dealer,
            "contract": final_bid,
            "declarer": declarer,
            "history": self.bidding_system.history,
        }

        # -------------------------------------------------
        # NAVIGATE TO PLAY
        # -------------------------------------------------

        if hasattr(
            window,
            "navigate"
        ):

            window.navigate(
                "Play"
            )

    # =====================================================
    # DISPLAY HELPERS
    # =====================================================

    @staticmethod
    def position_name(
        position
    ):

        return {
            Position.NORTH: "North",
            Position.EAST: "East",
            Position.SOUTH: "South",
            Position.WEST: "West",
        }[position]

    @staticmethod
    def bid_text(
        bid
    ):

        return (
            f"{bid.level}"
            f"{bid.denomination.short}"
        )

    # =====================================================
    # STYLE
    # =====================================================

    def get_style(self):

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
            color: #111111;
            border: none;
            border-radius: 5px;
            font-size: 15px;
            font-weight: bold;
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
            background-color: #1b3b2d;
        }

        QPushButton#secondaryButton:disabled {
            background-color: #11271d;
            color: #59645f;
            border: 1px solid #26342e;
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