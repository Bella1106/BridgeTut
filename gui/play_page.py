"""
Play screen for BridgeTut.

The GUI uses the existing Contract, declarer, play-validation,
and trick-resolution logic.

Flow:

    BiddingPage
        |
        | existing BiddingSystem
        v
    determine_contract()
        |
        v
    Contract
        |
        v
    PlayPage

The same deal created by BiddingPage is used for play.

Backend responsibilities:
    - Play validation
    - Led-suit determination
    - Trick winner determination
    - Contract/declarer logic

GUI responsibilities:
    - Display players and cards
    - Handle card clicks
    - Display tricks
    - Move turns
    - Start the next trick using the backend winner
    - Save completed tricks to GameRecord
"""

from PySide6.QtCore import Qt, QTimer, Signal
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

from card_model.card import Suit
from card_model.deck import new_deal
from card_model.player import Position

from game_logic.declarer import determine_opening_leader
from game_logic.play_validation import is_valid_play
from game_logic.trick_resolution import (
    determine_led_suit,
    determine_trick_winner,
)

from .widgets.player_seat import PlayerSeat
from .widgets.card_widget import CardWidget


class PlayPage(QWidget):

    # =====================================================
    # SIGNALS
    # =====================================================

    results_button_clicked = Signal()

    # =====================================================
    # INITIALISE
    # =====================================================

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

        self.game_record = None

        # =================================================
        # PLAY STATE
        # =================================================

        self.current_player = None

        self.played_cards = {}

        self.trick_number = 1

        self.game_complete = False

        self.trick_timer = None

        self.trick_winner = None

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

        # IMPORTANT:
        # Keep the backend trump Suit separate from
        # the centre trump QLabel.
        self.trump_suit = None

        self.trump = None

        self.trump_subtitle = None

        self.trick_slots = {}

        self.game_complete_label = None

        self.results_button = None

        self.setup_complete = False

        self.game_loaded = False

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

        data = None

        if hasattr(window, "play_data"):

            data = window.play_data

        # =================================================
        # LOAD DATA FROM BIDDING PAGE
        # =================================================

        if data is not None and not self.game_loaded:

            self.players = data.get("players")

            self.dealer = data.get("dealer")

            self.contract = data.get("contract")

            # =================================================
            # DECLARER
            # =================================================

            self.declarer = data.get("declarer")

            if self.contract is not None:

                contract_declarer = getattr(
                    self.contract,
                    "declarer",
                    None,
                )

                if contract_declarer is not None:

                    self.declarer = contract_declarer

            self.history = list(
                data.get(
                    "history",
                    [],
                )
            )

            # =================================================
            # RESET PLAY STATE
            # =================================================

            self.played_cards = {}

            self.trick_number = 1

            self.game_complete = False

            self.game_record = None

            self.trick_winner = None

            # =================================================
            # SET TRUMP
            # =================================================

            self.trump_suit = self.get_trump_suit()

            # =================================================
            # RESET COMPLETION UI
            # =================================================

            if self.game_complete_label is not None:

                self.game_complete_label.hide()

            if self.results_button is not None:

                self.results_button.setEnabled(False)

            # =================================================
            # GET OPENING LEADER
            # =================================================

            self.current_player = self.get_leader()

            # =================================================
            # CREATE GAME RECORD
            # =================================================

            self.create_game_record()

            self.game_loaded = True

        # =================================================
        # DEVELOPMENT FALLBACK
        # =================================================

        if self.players is None:

            self.dealer = Position.SOUTH

            self.players = new_deal(
                dealer=self.dealer,
                seed=42,
            )

            self.contract = None

            self.declarer = None

            self.history = []

            self.played_cards = {}

            self.trick_number = 1

            self.game_complete = False

            self.game_record = None

            self.trick_winner = None

            self.trump_suit = None

            self.current_player = None

            if self.game_complete_label is not None:

                self.game_complete_label.hide()

            if self.results_button is not None:

                self.results_button.setEnabled(False)

            self.create_game_record()

            self.game_loaded = True

        # =================================================
        # BUILD UI ONCE
        # =================================================

        if not self.setup_complete:

            self.setup_ui()

            self.setup_complete = True

        # =================================================
        # REFRESH UI
        # =================================================

        self.update_game_info()

        self.update_active_player()

        self.update_trick_area()

        self.update_playable_cards()

    # =====================================================
    # CREATE GAME RECORD
    # =====================================================

    def create_game_record(self):

        if self.game_record is not None:

            return

        window = self.window()

        if not hasattr(window, "history_manager"):

            print(
                "ERROR: Main window has no history_manager."
            )

            return

        self.game_record = (
            window.history_manager.add_game(
                dealer=self.dealer,
                players=self.players,
                contract=self.contract,
                declarer=self.declarer,
                bidding_history=list(
                    self.history
                ),
            )
        )

        print(
            f"GameRecord #{self.game_record.game_id} "
            f"created."
        )

    # =====================================================
    # RESET
    # =====================================================

    def reset_for_new_game(self):

        if self.trick_timer is not None:

            self.trick_timer.stop()

            self.trick_timer = None

        self.players = None

        self.dealer = None

        self.contract = None

        self.declarer = None

        self.history = []

        self.game_record = None

        self.current_player = None

        self.played_cards = {}

        self.trick_number = 1

        self.game_complete = False

        self.trick_winner = None

        self.trump_suit = None

        self.trump = None

        self.game_loaded = False

        if self.game_complete_label is not None:

            self.game_complete_label.hide()

        if self.results_button is not None:

            self.results_button.setEnabled(False)

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

        # =================================================
        # OPENING LEADER
        # =================================================

        opening_leader = self.get_leader()

        self.current_player = opening_leader

        # =================================================
        # PLAYER SEATS
        # =================================================

        north = PlayerSeat(
            self.players[Position.NORTH],
            role=self.player_role(Position.NORTH),
            active=(
                Position.NORTH
                == self.current_player
            ),
            dealer=False,
            hand_orientation="horizontal",
        )

        north.setFixedHeight(120)

        west = PlayerSeat(
            self.players[Position.WEST],
            role=self.player_role(Position.WEST),
            active=(
                Position.WEST
                == self.current_player
            ),
            dealer=False,
            hand_orientation="vertical",
        )

        west.setFixedWidth(155)

        east = PlayerSeat(
            self.players[Position.EAST],
            role=self.player_role(Position.EAST),
            active=(
                Position.EAST
                == self.current_player
            ),
            dealer=False,
            hand_orientation="vertical",
        )

        east.setFixedWidth(155)

        south = PlayerSeat(
            self.players[Position.SOUTH],
            role=self.player_role(Position.SOUTH),
            active=(
                Position.SOUTH
                == self.current_player
            ),
            dealer=False,
            hand_orientation="horizontal",
        )

        south.setFixedHeight(120)

        self.player_seats = {
            Position.NORTH: north,
            Position.EAST: east,
            Position.SOUTH: south,
            Position.WEST: west,
        }

        # =================================================
        # CARD CLICKS
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

        # =================================================
        # TRICK AREA
        # =================================================

        trick = self.create_trick_area()

        # =================================================
        # TABLE
        # =================================================

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

        table_layout.setColumnStretch(1, 1)
        table_layout.setColumnStretch(2, 1)
        table_layout.setColumnStretch(3, 1)
        table_layout.setRowStretch(1, 1)

        main_layout.addWidget(
            table,
            1,
        )

        # =================================================
        # SIDEBAR
        # =================================================

        sidebar = QWidget()

        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        sidebar_layout.setSpacing(14)

        # =================================================
        # CONTRACT
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
            "1 / 13",
            "trick_value",
        )

        sidebar_layout.addWidget(
            contract_panel
        )

        # =================================================
        # SCORES
        # =================================================

        scores = QHBoxLayout()

        scores.setSpacing(12)

        scores.addWidget(
            self.create_score_box(
                "DECLARER",
                "—",
                "SCORING LATER",
            )
        )

        scores.addWidget(
            self.create_score_box(
                "DEFENCE",
                "—",
                "SCORING LATER",
            )
        )

        sidebar_layout.addLayout(scores)

        # =================================================
        # GAME LOG
        # =================================================

        log = QFrame()

        log.setObjectName(
            "sidePanel"
        )

        log_layout = QVBoxLayout(log)

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

        self.game_log.setWordWrap(True)

        log_layout.addWidget(
            self.game_log
        )

        sidebar_layout.addWidget(
            log,
            1,
        )

        # =================================================
        # GAME COMPLETE
        # =================================================

        self.game_complete_label = QLabel(
            "GAME COMPLETE\n\n"
            "All 13 tricks have been played.\n"
            "The game has been saved to history."
        )

        self.game_complete_label.setObjectName(
            "gameComplete"
        )

        self.game_complete_label.setAlignment(
            Qt.AlignCenter
        )

        self.game_complete_label.setWordWrap(True)

        self.game_complete_label.hide()

        sidebar_layout.addWidget(
            self.game_complete_label
        )

        # =================================================
        # RESULTS
        # =================================================

        self.results_button = QPushButton(
            "VIEW RESULTS"
        )

        self.results_button.setObjectName(
            "resultsButton"
        )

        self.results_button.setFixedHeight(
            52
        )

        self.results_button.clicked.connect(
            self.results_button_clicked.emit
        )

        self.results_button.setEnabled(False)

        sidebar_layout.addWidget(
            self.results_button
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

        if self.game_complete:
            return

        if self.current_player is None:
            return

        if self.players is None:
            return

        if len(self.played_cards) >= 4:
            return

        player = self.players[
            self.current_player
        ]

        # =================================================
        # DETERMINE LED SUIT USING TEAM LOGIC
        # =================================================

        led_suit = determine_led_suit(
            self.played_cards
        )

        # =================================================
        # VALIDATE PLAY USING TEAM LOGIC
        # =================================================

        if not is_valid_play(
            player.hand,
            card,
            led_suit,
        ):

            seat = self.player_seats.get(
                self.current_player
            )

            if seat is not None:

                for card_widget in seat.cards:

                    if card_widget.card == card:

                        card_widget.mark_invalid()

                        break

            return

        print(
            f"{self.current_player.value} "
            f"played "
            f"{card.rank.short}"
            f"{card.suit.symbol}"
        )

        # =================================================
        # REMOVE CARD FROM HAND
        # =================================================

        player.hand.remove(card)

        # =================================================
        # STORE CARD
        # =================================================

        self.played_cards[
            self.current_player
        ] = card

        # =================================================
        # REFRESH HAND
        # =================================================

        seat = self.player_seats.get(
            self.current_player
        )

        if seat is not None:

            seat.rebuild_hand()

        # =================================================
        # REFRESH CENTRE
        # =================================================

        self.update_trick_area()

        # =================================================
        # FOUR CARDS = TRICK COMPLETE
        # =================================================

        if len(self.played_cards) == 4:

            self.trick_winner = (
                determine_trick_winner(
                    self.played_cards,
                    self.trump_suit,
                )
            )

            print(
                f"Trick {self.trick_number} "
                f"winner: "
                f"{self.position_name(self.trick_winner)}"
            )

            self.save_current_trick()

            # =============================================
            # TRICK 13
            # =============================================

            if self.trick_number >= 13:

                self.game_complete = True

                print(
                    "All 13 tricks completed."
                )

                if self.game_complete_label is not None:

                    self.game_complete_label.show()

                if self.results_button is not None:

                    self.results_button.setEnabled(
                        True
                    )

                self.update_active_player()

                self.update_game_info()

                self.update_playable_cards()

                return

            # =============================================
            # KEEP TRICK VISIBLE FOR 2 SECONDS
            # =============================================

            self.update_active_player()

            self.update_game_info()

            self.update_playable_cards()

            self.trick_timer = QTimer(self)

            self.trick_timer.setSingleShot(True)

            self.trick_timer.timeout.connect(
                self.start_next_trick
            )

            self.trick_timer.start(2000)

            return

        # =================================================
        # MOVE TO NEXT PLAYER
        # =================================================

        self.current_player = self.next_position(
            self.current_player
        )

        self.update_active_player()

        self.update_game_info()

        self.update_playable_cards()

    # =====================================================
    # UPDATE PLAYABLE CARDS
    # =====================================================

    def update_playable_cards(self):

        # Clear highlighting from every player first.
        for seat in self.player_seats.values():

            seat.clear_playable_cards()

        # Nothing should be highlighted when the game
        # has finished.
        if self.game_complete:
            return

        if self.current_player is None:
            return

        if self.players is None:
            return

        # Get the current player's actual hand.
        player = self.players[
            self.current_player
        ]

        # Determine the suit that was led.
        led_suit = determine_led_suit(
            self.played_cards
        )

        playable_cards = []

        # Use the existing backend validation logic
        # for every card.
        for card in player.hand.sorted_by_suit():

            if is_valid_play(
                player.hand,
                card,
                led_suit,
            ):

                playable_cards.append(card)

        # Apply the gold rim only to legal cards.
        seat = self.player_seats.get(
            self.current_player
        )

        if seat is not None:

            seat.set_playable_cards(
                playable_cards
            )

    # =====================================================
    # SAVE TRICK
    # =====================================================

    def save_current_trick(self):

        if self.game_record is None:

            self.create_game_record()

        if self.game_record is None:

            print(
                "ERROR: Cannot save trick."
            )

            return

        plays = dict(
            self.played_cards
        )

        if len(plays) != 4:

            print(
                "ERROR: Cannot save incomplete trick."
            )

            return

        self.game_record.add_trick(
            trick_number=self.trick_number,
            plays=plays,
        )

        print(
            f"Trick {self.trick_number} "
            f"saved to game history."
        )

    # =====================================================
    # START NEXT TRICK
    # =====================================================

    def start_next_trick(self):

        self.trick_timer = None

        # =================================================
        # THE WINNER OF THE PREVIOUS TRICK LEADS
        # THE NEXT TRICK
        # =================================================

        if self.trick_winner is None:

            print(
                "ERROR: No trick winner available."
            )

            return

        self.current_player = (
            self.trick_winner
        )

        self.trick_winner = None

        # =================================================
        # CLEAR PREVIOUS TRICK
        # =================================================

        self.played_cards = {}

        self.trick_number += 1

        self.update_trick_area()

        self.update_active_player()

        self.update_game_info()

        self.update_playable_cards()

    # =====================================================
    # NEXT POSITION
    # =====================================================

    @staticmethod
    def next_position(position):

        clockwise = {
            Position.SOUTH: Position.WEST,
            Position.WEST: Position.NORTH,
            Position.NORTH: Position.EAST,
            Position.EAST: Position.SOUTH,
        }

        return clockwise[position]

    # =====================================================
    # ACTIVE PLAYER
    # =====================================================

    def update_active_player(self):

        if not self.player_seats:
            return

        for position, seat in self.player_seats.items():

            is_active = (
                position == self.current_player
                and not self.game_complete
                and len(self.played_cards) < 4
            )

            seat.set_active(
                is_active
            )

            seat.setProperty(
                "playActive",
                is_active,
            )

            seat.style().unpolish(seat)
            seat.style().polish(seat)

            seat.update()

    # =====================================================
    # GAME INFO
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

        if self.dummy_value is not None:

            self.dummy_value.setText(
                self.position_name(
                    self.get_dummy()
                )
            )

        if self.leader_value is not None:

            self.leader_value.setText(
                self.position_name(
                    self.get_leader()
                )
            )

        if self.trick_value is not None:

            if self.game_complete:

                self.trick_value.setText(
                    "13 / 13"
                )

            else:

                cards_played = len(
                    self.played_cards
                )

                self.trick_value.setText(
                    f"{self.trick_number} / 13 "
                    f"({cards_played}/4)"
                )

        self.update_trump_display()

        self.update_game_log()

    # =====================================================
    # CONTRACT DISPLAY
    # =====================================================

    def contract_text(self):

        if self.contract is None:

            return "No Contract"

        return (
            f"{self.contract.level}"
            f"{self.denomination_short()}"
            f" by "
            f"{self.position_letter(self.declarer)}"
        )

    # =====================================================
    # TRUMP SUIT
    # =====================================================

    def get_trump_suit(self):

        if self.contract is None:

            return None

        denomination = (
            self.contract.denomination
        )

        # =================================================
        # NO TRUMP
        # =================================================

        if denomination == Denomination.NO_TRUMP:

            return None

        # =================================================
        # DENOMINATION -> SUIT
        # =================================================

        denomination_map = {
            Denomination.CLUBS: Suit.CLUBS,
            Denomination.DIAMONDS: Suit.DIAMONDS,
            Denomination.HEARTS: Suit.HEARTS,
            Denomination.SPADES: Suit.SPADES,
        }

        return denomination_map.get(
            denomination
        )

    # =====================================================
    # TRUMP DISPLAY
    # =====================================================

    def update_trump_display(self):

        if self.contract is None:
            return

        denomination = (
            self.contract.denomination
        )

        symbol_map = {
            Denomination.CLUBS: "♣",
            Denomination.DIAMONDS: "♦",
            Denomination.HEARTS: "♥",
            Denomination.SPADES: "♠",
            Denomination.NO_TRUMP: "NT",
        }

        symbol = symbol_map.get(
            denomination,
            "?",
        )

        # self.trump is the centre QLabel.
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

        tricks_saved = 0

        if self.game_record is not None:

            tricks_saved = (
                self.game_record.tricks_played
            )

        if self.game_complete:

            status = (
                "> 13 tricks completed.\n\n"
                "> Complete game saved to history.\n\n"
                f"> {tricks_saved}/13 tricks recorded."
            )

        else:

            status = (
                f"> Current turn: "
                f"{current_letter}.\n\n"
                f"> {tricks_saved} trick(s) "
                f"saved to history."
            )

        self.game_log.setText(
            f"> Cards dealt. "
            f"{dealer_letter} is the dealer.\n\n"
            f"> Bidding complete — "
            f"{contract_text}.\n\n"
            f"> {leader_letter} leads to trick 1.\n\n"
            f"> Trick {self.trick_number} of 13.\n\n"
            f"{status}"
        )

    # =====================================================
    # PLAYER ROLE
    # =====================================================

    def player_role(self, position):

        if self.declarer is None:

            return "Defender"

        if position == self.declarer:

            return "Declarer"

        if position == self.get_partner(
            self.declarer
        ):

            return "Dummy"

        return "Defender"

    # =====================================================
    # PARTNER
    # =====================================================

    @staticmethod
    def get_partner(position):

        partners = {
            Position.NORTH: Position.SOUTH,
            Position.SOUTH: Position.NORTH,
            Position.EAST: Position.WEST,
            Position.WEST: Position.EAST,
        }

        return partners.get(position)

    # =====================================================
    # DUMMY
    # =====================================================

    def get_dummy(self):

        if self.declarer is None:

            return None

        return self.get_partner(
            self.declarer
        )

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
            "short",
        ):

            return denomination.short

        return {
            Denomination.CLUBS: "C",
            Denomination.DIAMONDS: "D",
            Denomination.HEARTS: "H",
            Denomination.SPADES: "S",
            Denomination.NO_TRUMP: "NT",
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
            Position.NORTH: "North",
            Position.EAST: "East",
            Position.SOUTH: "South",
            Position.WEST: "West",
        }[position]

    @staticmethod
    def position_letter(position):

        if position is None:

            return "?"

        return {
            Position.NORTH: "N",
            Position.EAST: "E",
            Position.SOUTH: "S",
            Position.WEST: "W",
        }[position]

    # =====================================================
    # TRICK AREA
    # =====================================================

    def create_trick_area(self):

        container = QWidget()

        grid = QGridLayout(container)

        grid.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        grid.setSpacing(12)

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

        self.trick_slots = {
            Position.NORTH: north,
            Position.WEST: west,
            Position.EAST: east,
            Position.SOUTH: south,
        }

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
            100,
        )

        slot.position = position

        return slot

    # =====================================================
    # UPDATE TRICK AREA
    # =====================================================

    def update_trick_area(self):

        for position, slot in self.trick_slots.items():

            for child in slot.findChildren(
                CardWidget
            ):

                child.deleteLater()

            if position not in self.played_cards:

                continue

            card = self.played_cards[position]

            card_widget = CardWidget(card)

            card_widget.setEnabled(False)

            card_widget.setParent(slot)

            card_widget.move(
                14,
                16,
            )

            card_widget.show()

    # =====================================================
    # TRUMP LABEL
    # =====================================================

    def trump_label(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)

        layout.setAlignment(
            Qt.AlignCenter
        )

        # This is the DISPLAY LABEL only.
        # The actual backend trump is self.trump_suit.
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

        left = QLabel(label)

        left.setObjectName(
            "sideLabel"
        )

        right = QLabel(value)

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
                right,
            )

        row.addWidget(left)

        row.addWidget(right)

        layout.addLayout(row)

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

        layout = QVBoxLayout(box)

        layout.setAlignment(
            Qt.AlignCenter
        )

        title_label = QLabel(title)

        title_label.setObjectName(
            "scoreTitle"
        )

        score_label = QLabel(score)

        score_label.setObjectName(
            "score"
        )

        needed_label = QLabel(needed)

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
        }

        QLabel#score {
            color: #e5c557;
            font-size: 30px;
            font-weight: bold;
        }

        QLabel#needed {
            color: #b9c8c1;
            font-size: 12px;
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
        }

        QLabel#logTitle {
            color: #b9c8c1;
            font-size: 12px;
        }

        QLabel#gameLog {
            color: #d1dbd5;
            font-family: Consolas, monospace;
            font-size: 12px;
        }

        QLabel#gameComplete {
            background-color: #11271d;
            color: #e5c557;
            border: 1px solid #e5c557;
            border-radius: 8px;
            padding: 14px;
            font-size: 14px;
            font-weight: bold;
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

        QPushButton#resultsButton:disabled {
            background-color: #29483b;
            color: #71847b;
        }

        """