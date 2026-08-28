"""
Play screen for BridgeTut.

Temporary play implementation.

For this stage we are intentionally NOT implementing:

- play_validation
- trick_resolution
- following-suit rules
- trump rules
- trick winners
- scoring

The current behaviour is simply:

    1. Opening leader is activated.
    2. User clicks a card.
    3. Card is removed from the player's hand.
    4. Card appears in the centre.
    5. Turn moves clockwise.
    6. The next player's cards become clickable.
    7. After the fourth card is played, all four cards
       remain visible for 2 seconds.
    8. The centre is cleared for the next trick.

This gives us a working interactive Play page while the
play-validation and trick-resolution modules are developed
separately.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
)

from bidding.bid import Denomination

from card_model.deck import new_deal
from card_model.player import Position

from game_logic.declarer import determine_opening_leader

from .widgets.player_seat import PlayerSeat
from .widgets.card_widget import CardWidget


class PlayPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # =================================================
        # GAME DATA
        # =================================================

        self.players = None
        self.dealer = None
        self.contract = None
        self.declarer = None
        self.history = []

        # =================================================
        # PLAY STATE
        # =================================================

        # Player whose turn it currently is.
        self.current_player = None

        # Cards currently displayed in the centre.
        #
        # Example:
        #
        # {
        #     Position.WEST: card,
        #     Position.NORTH: card,
        # }
        #
        self.played_cards = {}

        # =================================================
        # UI
        # =================================================

        self.player_seats = {}

        self.contract_title = None
        self.declarer_value = None
        self.dummy_value = None
        self.leader_value = None
        self.trick_value = None
        self.game_log = None

        self.trump = None
        self.trump_subtitle = None

        # Central trick card slots.
        self.trick_slots = {}

        self.setup_complete = False

    # =====================================================
    # SHOW EVENT
    # =====================================================

    def showEvent(self, event):

        super().showEvent(event)

        self.load_game()

    # =====================================================
    # LOAD GAME
    # =====================================================

    def load_game(self):

        window = self.window()

        # -------------------------------------------------
        # GET DATA FROM BIDDING
        # -------------------------------------------------

        if hasattr(window, "play_data"):

            data = window.play_data

            if data is not None:

                self.players = data.get(
                    "players"
                )

                self.dealer = data.get(
                    "dealer"
                )

                self.contract = data.get(
                    "contract"
                )

                self.declarer = data.get(
                    "declarer"
                )

                self.history = data.get(
                    "history",
                    []
                )

        # -------------------------------------------------
        # FALLBACK DEAL
        # -------------------------------------------------

        if self.players is None:

            self.dealer = Position.SOUTH

            self.players = new_deal(
                dealer=self.dealer,
                seed=42,
            )

        # -------------------------------------------------
        # DETERMINE FIRST PLAYER
        # -------------------------------------------------

        leader = self.get_leader()

        if leader is not None:

            self.current_player = leader

        else:

            # Development fallback.
            #
            # If there is no contract/declarer yet,
            # South starts temporarily.
            self.current_player = Position.SOUTH

        # -------------------------------------------------
        # RESET PLAYED CARDS
        # -------------------------------------------------

        self.played_cards = {}

        # -------------------------------------------------
        # BUILD UI
        # -------------------------------------------------

        if not self.setup_complete:

            self.setup_ui()

            self.setup_complete = True

        # -------------------------------------------------
        # UPDATE
        # -------------------------------------------------

        self.update_game_info()

        self.update_active_player()

    # =====================================================
    # SETUP UI
    # =====================================================

    def setup_ui(self):

        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(
            4,
            8,
            8,
            8,
        )

        main_layout.setSpacing(14)

        # =================================================
        # TABLE
        # =================================================

        table = QFrame()

        table.setObjectName(
            "playTable"
        )

        table_layout = QGridLayout(table)

        table_layout.setContentsMargins(
            14,
            14,
            14,
            14,
        )

        table_layout.setSpacing(0)

        # -------------------------------------------------
        # OPENING LEADER
        # -------------------------------------------------

        opening_leader = self.get_leader()

        if opening_leader is None:

            opening_leader = Position.SOUTH

        self.current_player = opening_leader

        # -------------------------------------------------
        # NORTH
        # -------------------------------------------------

        north = PlayerSeat(
            self.players[Position.NORTH],
            role=self.player_role(
                Position.NORTH
            ),
            active=(
                Position.NORTH
                == self.current_player
            ),
            dealer=False,
            hand_orientation="horizontal",
        )

        north.setFixedHeight(
            120
        )

        # -------------------------------------------------
        # WEST
        # -------------------------------------------------

        west = PlayerSeat(
            self.players[Position.WEST],
            role=self.player_role(
                Position.WEST
            ),
            active=(
                Position.WEST
                == self.current_player
            ),
            dealer=False,
            hand_orientation="vertical",
        )

        west.setFixedWidth(
            155
        )

        # -------------------------------------------------
        # EAST
        # -------------------------------------------------

        east = PlayerSeat(
            self.players[Position.EAST],
            role=self.player_role(
                Position.EAST
            ),
            active=(
                Position.EAST
                == self.current_player
            ),
            dealer=False,
            hand_orientation="vertical",
        )

        east.setFixedWidth(
            155
        )

        # -------------------------------------------------
        # SOUTH
        # -------------------------------------------------

        south = PlayerSeat(
            self.players[Position.SOUTH],
            role=self.player_role(
                Position.SOUTH
            ),
            active=(
                Position.SOUTH
                == self.current_player
            ),
            dealer=False,
            hand_orientation="horizontal",
        )

        south.setFixedHeight(
            120
        )

        # -------------------------------------------------
        # STORE SEATS
        # -------------------------------------------------

        self.player_seats = {

            Position.NORTH:
                north,

            Position.EAST:
                east,

            Position.SOUTH:
                south,

            Position.WEST:
                west,
        }

        # =================================================
        # CONNECT CARD CLICKS
        # =================================================

        north.card_clicked.connect(
            self.play_card
        )

        east.card_clicked.connect(
            self.play_card
        )

        south.card_clicked.connect(
            self.play_card
        )

        west.card_clicked.connect(
            self.play_card
        )

        # -------------------------------------------------
        # TRICK AREA
        # -------------------------------------------------

        trick = self.create_trick_area()

        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        table_layout.addWidget(
            north,
            0,
            1,
            1,
            3,
        )

        table_layout.addWidget(
            west,
            1,
            0,
        )

        table_layout.addWidget(
            trick,
            1,
            1,
            1,
            3,
        )

        table_layout.addWidget(
            east,
            1,
            4,
        )

        table_layout.addWidget(
            south,
            2,
            1,
            1,
            3,
        )

        table_layout.setColumnStretch(
            1,
            1,
        )

        table_layout.setColumnStretch(
            2,
            1,
        )

        table_layout.setColumnStretch(
            3,
            1,
        )

        table_layout.setRowStretch(
            1,
            1,
        )

        main_layout.addWidget(
            table,
            1,
        )

        # =================================================
        # SIDEBAR
        # =================================================

        sidebar = QWidget()

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        sidebar_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        sidebar_layout.setSpacing(
            14
        )

        # =================================================
        # CONTRACT PANEL
        # =================================================

        contract_panel = QFrame()

        contract_panel.setObjectName(
            "sidePanel"
        )

        contract_layout = QVBoxLayout(
            contract_panel
        )

        contract_layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        self.contract_title = QLabel(
            self.contract_text()
        )

        self.contract_title.setObjectName(
            "contractTitle"
        )

        contract_layout.addWidget(
            self.contract_title
        )

        self.add_side_row(
            contract_layout,
            "DECLARER",
            self.position_name(
                self.declarer
            ),
            "declarer_value",
        )

        self.add_side_row(
            contract_layout,
            "DUMMY",
            self.position_name(
                self.get_dummy()
            ),
            "dummy_value",
        )

        self.add_side_row(
            contract_layout,
            "OPENING LEAD",
            self.position_name(
                self.get_leader()
            ),
            "leader_value",
        )

        self.add_side_row(
            contract_layout,
            "TRICK",
            "0 / 4",
            "trick_value",
        )

        sidebar_layout.addWidget(
            contract_panel
        )

        # =================================================
        # SCORES
        # =================================================

        scores = QHBoxLayout()

        scores.setSpacing(
            12
        )

        scores.addWidget(
            self.create_score_box(
                "DECLARER",
                "0",
                "NEED 10",
            )
        )

        scores.addWidget(
            self.create_score_box(
                "DEFENCE",
                "0",
                "NEED 4",
            )
        )

        sidebar_layout.addLayout(
            scores
        )

        # =================================================
        # GAME LOG
        # =================================================

        log = QFrame()

        log.setObjectName(
            "sidePanel"
        )

        log_layout = QVBoxLayout(
            log
        )

        log_layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        log_title = QLabel(
            "GAME LOG"
        )

        log_title.setObjectName(
            "logTitle"
        )

        log_layout.addWidget(
            log_title
        )

        self.game_log = QLabel()

        self.game_log.setObjectName(
            "gameLog"
        )

        self.game_log.setWordWrap(
            True
        )

        log_layout.addWidget(
            self.game_log
        )

        sidebar_layout.addWidget(
            log,
            1,
        )

        # =================================================
        # RESULTS
        # =================================================

        results = QPushButton(
            "Results"
        )

        results.setObjectName(
            "resultsButton"
        )

        results.setFixedHeight(
            52
        )

        sidebar_layout.addWidget(
            results
        )

        main_layout.addWidget(
            sidebar,
            0,
        )

        self.setStyleSheet(
            self.get_style()
        )

        self.update_active_player()

    # =====================================================
    # PLAY CARD
    # =====================================================

    def play_card(self, card):

        # -------------------------------------------------
        # Make sure we have a current player.
        # -------------------------------------------------

        if self.current_player is None:

            return

        # -------------------------------------------------
        # Get current player.
        # -------------------------------------------------

        player = self.players[
            self.current_player
        ]

        # -------------------------------------------------
        # Make sure the clicked card belongs to
        # the player whose turn it is.
        #
        # This is NOT play validation.
        #
        # It simply prevents an invalid GUI signal
        # from removing another player's card.
        # -------------------------------------------------

        if card not in player.hand:

            return

        # -------------------------------------------------
        # DEBUG OUTPUT
        # -------------------------------------------------

        print(
            f"{self.current_player.value} attempted "
            f"to play "
            f"{card.rank.short}{card.suit.symbol}"
        )

        # -------------------------------------------------
        # REMOVE CARD FROM HAND
        # -------------------------------------------------

        player.hand.remove(card)

        # -------------------------------------------------
        # STORE CARD IN CENTRE
        # -------------------------------------------------

        self.played_cards[
            self.current_player
        ] = card

        # -------------------------------------------------
        # UPDATE PLAYER'S HAND
        # -------------------------------------------------

        seat = self.player_seats[
            self.current_player
        ]

        seat.rebuild_hand()

        # -------------------------------------------------
        # DISPLAY CARD IN CENTRE
        # -------------------------------------------------

        self.update_trick_area()

        # -------------------------------------------------
        # MOVE CLOCKWISE
        #
        # South -> West -> North -> East -> South
        # -------------------------------------------------

        self.current_player = (
            self.next_position(
                self.current_player
            )
        )

        # -------------------------------------------------
        # UPDATE ACTIVE PLAYER
        # -------------------------------------------------

        self.update_active_player()

        # -------------------------------------------------
        # UPDATE INFO
        # -------------------------------------------------

        self.update_game_info()

        # -------------------------------------------------
        # FOURTH CARD
        # -------------------------------------------------
        #
        # Once all four players have played:
        #
        # - Leave all four cards visible.
        # - Wait exactly 2 seconds.
        # - Clear the centre.
        #
        # We deliberately do NOT determine a winner.
        # -------------------------------------------------

        if len(self.played_cards) == 4:

            QTimer.singleShot(
                2000,
                self.clear_trick_area
            )

    # =====================================================
    # CLEAR TRICK AREA
    # =====================================================

    def clear_trick_area(self):

        # -------------------------------------------------
        # Clear the cards currently displayed in the centre.
        #
        # No trick winner is calculated.
        # -------------------------------------------------

        self.played_cards = {}

        self.update_trick_area()

        # Update the temporary counter.
        self.update_game_info()

    # =====================================================
    # NEXT POSITION
    # =====================================================

    @staticmethod
    def next_position(position):

        clockwise = {

            Position.SOUTH:
                Position.WEST,

            Position.WEST:
                Position.NORTH,

            Position.NORTH:
                Position.EAST,

            Position.EAST:
                Position.SOUTH,
        }

        return clockwise[position]

    # =====================================================
    # UPDATE ACTIVE PLAYER
    # =====================================================

    def update_active_player(self):

        if not self.player_seats:

            return

        for position, seat in self.player_seats.items():

            is_active = (
                position
                == self.current_player
            )

            seat.set_active(
                is_active
            )

            seat.setProperty(
                "playActive",
                is_active
            )

            seat.style().unpolish(seat)
            seat.style().polish(seat)
            seat.update()

    # =====================================================
    # UPDATE GAME INFO
    # =====================================================

    def update_game_info(self):

        if self.contract_title is None:

            return

        self.contract_title.setText(
            self.contract_text()
        )

        if self.declarer_value is not None:

            self.declarer_value.setText(
                self.position_name(
                    self.declarer
                )
            )

        dummy = self.get_dummy()

        if self.dummy_value is not None:

            self.dummy_value.setText(
                self.position_name(
                    dummy
                )
            )

        leader = self.get_leader()

        if self.leader_value is not None:

            self.leader_value.setText(
                self.position_name(
                    leader
                )
            )

        # -------------------------------------------------
        # TEMPORARY TRICK DISPLAY
        #
        # We are NOT calculating trick winners.
        # -------------------------------------------------

        if self.trick_value is not None:

            cards_played = len(
                self.played_cards
            )

            self.trick_value.setText(
                f"{cards_played} / 4"
            )

        self.update_trump_display()

        self.update_game_log()

    # =====================================================
    # CONTRACT TEXT
    # =====================================================

    def contract_text(self):

        if self.contract is None:

            return "No Contract"

        declarer = getattr(
            self.contract,
            "declarer",
            self.declarer,
        )

        return (
            f"{self.contract.level}"
            f"{self.denomination_short()}"
            f" by {self.position_letter(declarer)}"
        )

    # =====================================================
    # TRUMP
    # =====================================================

    def update_trump_display(self):

        if self.contract is None:

            return

        denomination = (
            self.contract.denomination
        )

        symbol_map = {

            Denomination.CLUBS:
                "♣",

            Denomination.DIAMONDS:
                "♦",

            Denomination.HEARTS:
                "♥",

            Denomination.SPADES:
                "♠",

            Denomination.NO_TRUMP:
                "NT",
        }

        symbol = symbol_map.get(
            denomination,
            "?",
        )

        if self.trump is not None:

            self.trump.setText(
                symbol
            )

        if self.trump_subtitle is not None:

            if denomination == Denomination.NO_TRUMP:

                self.trump_subtitle.setText(
                    "NO TRUMP"
                )

            else:

                self.trump_subtitle.setText(
                    "TRUMP"
                )

    # =====================================================
    # GAME LOG
    # =====================================================

    def update_game_log(self):

        if self.game_log is None:

            return

        dealer_letter = (
            self.position_letter(
                self.dealer
            )
            if self.dealer is not None
            else "—"
        )

        contract_text = (
            self.contract_text()
            if self.contract is not None
            else "No contract"
        )

        leader = self.get_leader()

        leader_letter = (
            self.position_letter(
                leader
            )
            if leader is not None
            else "—"
        )

        current_letter = (
            self.position_letter(
                self.current_player
            )
            if self.current_player is not None
            else "—"
        )

        self.game_log.setText(

            f"> Cards dealt. "
            f"{dealer_letter} is the dealer and bids first.\n\n"

            f"> Bidding complete — "
            f"{contract_text}.\n\n"

            f"> {leader_letter} leads to trick 1.\n\n"

            f"> Current turn: "
            f"{current_letter}."
        )

    # =====================================================
    # PLAYER ROLE
    # =====================================================

    def player_role(self, position):

        if self.declarer is None:

            return "Defender"

        if position == self.declarer:

            return "Declarer"

        if position == self.get_dummy():

            return "Dummy"

        return "Defender"

    # =====================================================
    # DUMMY
    # =====================================================

    def get_dummy(self):

        if self.contract is not None:

            if hasattr(
                self.contract,
                "dummy"
            ):

                return self.contract.dummy

        if self.declarer is None:

            return None

        return self.declarer.partner

    # =====================================================
    # OPENING LEADER
    # =====================================================

    def get_leader(self):

        if self.declarer is None:

            return None

        return determine_opening_leader(
            self.declarer
        )

    # =====================================================
    # DENOMINATION
    # =====================================================

    def denomination_short(self):

        if self.contract is None:

            return ""

        denomination = (
            self.contract.denomination
        )

        if hasattr(
            denomination,
            "short"
        ):

            return denomination.short

        return {

            Denomination.CLUBS:
                "C",

            Denomination.DIAMONDS:
                "D",

            Denomination.HEARTS:
                "H",

            Denomination.SPADES:
                "S",

            Denomination.NO_TRUMP:
                "NT",

        }.get(
            denomination,
            "?",
        )

    # =====================================================
    # POSITION HELPERS
    # =====================================================

    @staticmethod
    def position_name(position):

        if position is None:

            return "—"

        return {

            Position.NORTH:
                "North",

            Position.EAST:
                "East",

            Position.SOUTH:
                "South",

            Position.WEST:
                "West",

        }[position]

    @staticmethod
    def position_letter(position):

        if position is None:

            return "?"

        return {

            Position.NORTH:
                "N",

            Position.EAST:
                "E",

            Position.SOUTH:
                "S",

            Position.WEST:
                "W",

        }[position]

    # =====================================================
    # TRICK AREA
    # =====================================================

    def create_trick_area(self):

        container = QWidget()

        grid = QGridLayout(
            container
        )

        grid.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        grid.setSpacing(
            12
        )

        # -------------------------------------------------
        # CREATE FOUR CARD SLOTS
        # -------------------------------------------------

        north = self.trick_slot(
            Position.NORTH
        )

        west = self.trick_slot(
            Position.WEST
        )

        centre = self.trump_label()

        east = self.trick_slot(
            Position.EAST
        )

        south = self.trick_slot(
            Position.SOUTH
        )

        # -------------------------------------------------
        # STORE SLOTS
        # -------------------------------------------------

        self.trick_slots = {

            Position.NORTH:
                north,

            Position.WEST:
                west,

            Position.EAST:
                east,

            Position.SOUTH:
                south,
        }

        # -------------------------------------------------
        # POSITION SLOTS
        # -------------------------------------------------

        grid.addWidget(
            north,
            0,
            1,
        )

        grid.addWidget(
            west,
            1,
            0,
        )

        grid.addWidget(
            centre,
            1,
            1,
        )

        grid.addWidget(
            east,
            1,
            2,
        )

        grid.addWidget(
            south,
            2,
            1,
        )

        return container

    # =====================================================
    # TRICK SLOT
    # =====================================================

    def trick_slot(self, position):

        slot = QFrame()

        slot.setObjectName(
            "trickSlot"
        )

        slot.setFixedSize(
            70,
            100
        )

        # Keep track of which player owns this slot.
        slot.position = position

        return slot

    # =====================================================
    # UPDATE TRICK AREA
    # =====================================================

    def update_trick_area(self):

        for position, slot in self.trick_slots.items():

            # Remove existing child widgets.
            for child in slot.findChildren(
                CardWidget
            ):

                child.deleteLater()

            # -------------------------------------------------
            # Nothing played here yet.
            # -------------------------------------------------

            if position not in self.played_cards:

                continue

            card = self.played_cards[
                position
            ]

            # -------------------------------------------------
            # Create a card widget for the centre.
            #
            # This is display-only.
            # -------------------------------------------------

            card_widget = CardWidget(
                card
            )

            card_widget.setEnabled(
                False
            )

            card_widget.setParent(
                slot
            )

            card_widget.move(
                14,
                16
            )

            card_widget.show()

    # =====================================================
    # TRUMP LABEL
    # =====================================================

    def trump_label(self):

        widget = QWidget()

        layout = QVBoxLayout(
            widget
        )

        layout.setAlignment(
            Qt.AlignCenter
        )

        self.trump = QLabel(
            "NT"
        )

        self.trump.setObjectName(
            "trump"
        )

        self.trump.setAlignment(
            Qt.AlignCenter
        )

        self.trump_subtitle = QLabel(
            "TRUMP"
        )

        self.trump_subtitle.setObjectName(
            "trumpSubtitle"
        )

        self.trump_subtitle.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.trump
        )

        layout.addWidget(
            self.trump_subtitle
        )

        return widget

    # =====================================================
    # SIDEBAR ROW
    # =====================================================

    def add_side_row(
        self,
        layout,
        label,
        value,
        key=None,
    ):

        row = QHBoxLayout()

        left = QLabel(
            label
        )

        left.setObjectName(
            "sideLabel"
        )

        right = QLabel(
            value
        )

        right.setObjectName(
            "sideValue"
        )

        right.setAlignment(
            Qt.AlignRight
        )

        if key is not None:

            setattr(
                self,
                key,
                right
            )

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
    # SCORE BOX
    # =====================================================

    def create_score_box(
        self,
        title,
        score,
        needed,
    ):

        box = QFrame()

        box.setObjectName(
            "scoreBox"
        )

        layout = QVBoxLayout(
            box
        )

        layout.setAlignment(
            Qt.AlignCenter
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "scoreTitle"
        )

        score_label = QLabel(
            score
        )

        score_label.setObjectName(
            "score"
        )

        needed_label = QLabel(
            needed
        )

        needed_label.setObjectName(
            "needed"
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            score_label
        )

        layout.addWidget(
            needed_label
        )

        return box

    # =====================================================
    # STYLE
    # =====================================================

    def get_style(self):

        return """

        QWidget {
            font-family: "Segoe UI", Arial, sans-serif;
        }

        QFrame#playTable {
            background-color: #00602e;
            border-radius: 12px;
        }

        QFrame#playerSeat {
            background-color: #00582b;
            border-radius: 10px;
        }

        /* ================================================
           ACTIVE PLAYER
           ================================================ */

        QFrame#playerSeat[playActive="true"] {
            border: 3px solid #e5c557;
            border-radius: 10px;
        }

        QFrame#playerSeat[playActive="false"] {
            border: 1px solid transparent;
            border-radius: 10px;
        }

        QFrame#sidePanel,
        QFrame#scoreBox {
            background-color: #11271d;
            border: 1px solid #29483b;
            border-radius: 10px;
        }

        QLabel {
            color: #f1f4f2;
        }

        QLabel#contractTitle {
            color: #e5c557;
            font-family: Georgia, serif;
            font-size: 23px;
            font-weight: bold;
            padding-bottom: 6px;
        }

        QLabel#sideLabel {
            color: #b9c8c1;
            font-size: 12px;
            letter-spacing: 1px;
            padding: 5px 0px;
        }

        QLabel#sideValue {
            color: white;
            font-size: 13px;
            font-weight: bold;
        }

        QFrame#scoreBox {
            min-height: 105px;
        }

        QLabel#scoreTitle {
            color: #b9c8c1;
            font-size: 12px;
            letter-spacing: 1px;
        }

        QLabel#score {
            color: #e5c557;
            font-size: 30px;
            font-weight: bold;
        }

        QLabel#needed {
            color: #b9c8c1;
            font-size: 12px;
            letter-spacing: 1px;
        }

        QFrame#trickSlot {
            background-color: transparent;
            border: 2px dashed #003f22;
            border-radius: 8px;
        }

        QLabel#trump {
            color: #e5c557;
            font-size: 28px;
            font-weight: bold;
        }

        QLabel#trumpSubtitle {
            color: #b9c8c1;
            font-size: 12px;
            letter-spacing: 1px;
        }

        QLabel#logTitle {
            color: #b9c8c1;
            font-size: 12px;
            letter-spacing: 1px;
        }

        QLabel#gameLog {
            color: #d1dbd5;
            font-family: Consolas, monospace;
            font-size: 12px;
        }

        QPushButton#resultsButton {
            background-color: #51b5ba;
            color: #071710;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: bold;
        }

        QPushButton#resultsButton:hover {
            background-color: #68c4c8;
        }

        """
