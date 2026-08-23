"""
Play screen for BridgeTut.

Displays the four hands and the central trick area.

The Play page does not create a new deal when a completed auction
has been supplied by the main window. It uses the same players/deal
that was used during bidding and displays the actual contract and
declarer.

Expected data on the main window:

    window.play_data = {
        "players": self.players,
        "dealer": self.dealer,
        "contract": final_bid,
        "declarer": declarer,
        "history": self.bidding_system.history,
    }

A fallback deal is kept so that the Play page can still be opened
directly while the rest of the application is being developed.
"""

from bidding.bid import Denomination
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
)

from card_model.deck import new_deal
from card_model.player import Position

from .widgets.player_seat import PlayerSeat


class PlayPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Game data supplied by BiddingPage/MainWindow.
        self.players = None
        self.dealer = None
        self.contract = None
        self.declarer = None
        self.history = []
        self.current_player = None

        self.player_seats = {}

        # References to labels that must change when a game is loaded.
        self.contract_title = None
        self.declarer_value = None
        self.leader_value = None
        self.trick_value = None
        self.game_log = None
        self.trump = None
        self.trump_subtitle = None

        self.setup_complete = False

    # =====================================================
    # LOAD GAME
    # =====================================================

    def showEvent(self, event):

        super().showEvent(event)

        self.load_game()

    def load_game(self):

        window = self.window()

        # -------------------------------------------------
        # USE THE GAME CREATED DURING BIDDING
        # -------------------------------------------------

        if hasattr(window, "play_data"):

            data = window.play_data

            self.players = data.get("players")
            self.dealer = data.get("dealer")
            self.contract = data.get("contract")
            self.declarer = data.get("declarer")
            self.history = data.get("history", [])
            
            print("PLAY CONTRACT:", self.contract)
            print("PLAY DECLARER:", self.declarer)
        # -------------------------------------------------
        # FALLBACK FOR OPENING PLAY DIRECTLY
        # -------------------------------------------------
        #
        # This keeps the page visible while the project is
        # being developed. It is NOT used when play_data
        # has been supplied by BiddingPage.
        #

        if self.players is None:

            self.dealer = Position.SOUTH

            self.players = new_deal(
                dealer=self.dealer,
                seed=42,
            )

        # -------------------------------------------------
        # CREATE THE UI ONLY AFTER WE HAVE A DEAL
        # -------------------------------------------------

        if not self.setup_complete:

            self.setup_ui()

            self.setup_complete = True

        # -------------------------------------------------
        # UPDATE DYNAMIC GAME INFORMATION
        # -------------------------------------------------
        self.current_player = self.get_leader()
        self.update_game_info()
    def update_active_player(self):

        for position, seat in self.player_seats.items():

            seat.set_active(
                position == self.current_player
            )
    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(
            4,
            8,
            8,
            8
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
            14
        )

        table_layout.setSpacing(0)

        # -------------------------------------------------
        # DETERMINE PLAYER ROLES
        # -------------------------------------------------

        north = PlayerSeat(
            self.players[Position.NORTH],
            role=self.player_role(Position.NORTH),
            hand_orientation="horizontal",
        )

        north.setFixedHeight(120)

        west = PlayerSeat(
            self.players[Position.WEST],
            role=self.player_role(Position.WEST),
            hand_orientation="vertical",
        )

        west.setFixedWidth(155)

        east = PlayerSeat(
            self.players[Position.EAST],
            role=self.player_role(Position.EAST),
            hand_orientation="vertical",
        )

        east.setFixedWidth(155)

        south = PlayerSeat(
            self.players[Position.SOUTH],
            role=self.player_role(Position.SOUTH),
            active=False,
            hand_orientation="horizontal",
        )

        south.setFixedHeight(120)

        self.player_seats = {
            Position.NORTH: north,
            Position.EAST: east,
            Position.SOUTH: south,
            Position.WEST: west,
        }

        # -------------------------------------------------
        # CENTRE TRICK
        # -------------------------------------------------

        trick = self.create_trick_area()

        # -------------------------------------------------
        # TABLE POSITIONS
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
            1
        )

        table_layout.setColumnStretch(
            2,
            1
        )

        table_layout.setColumnStretch(
            3,
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
        # RIGHT SIDEBAR
        # =================================================

        sidebar = QWidget()

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        sidebar_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        sidebar_layout.setSpacing(14)

        # -------------------------------------------------
        # CONTRACT
        # -------------------------------------------------

        contract = QFrame()

        contract.setObjectName(
            "sidePanel"
        )

        contract_layout = QVBoxLayout(
            contract
        )

        contract_layout.setContentsMargins(
            16,
            14,
            16,
            14
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
            self.position_name(self.declarer)
            if self.declarer is not None
            else "—",
            "declarer_value"
        )

        leader = self.get_leader()

        self.add_side_row(
            contract_layout,
            "LEAD / TURN",
            self.position_name(leader)
            if leader is not None
            else "—",
            "leader_value"
        )

        self.add_side_row(
            contract_layout,
            "TRICK",
            "1 / 13",
            "trick_value"
        )

        sidebar_layout.addWidget(
            contract
        )

        # -------------------------------------------------
        # SCORE BOXES
        # -------------------------------------------------

        scores = QHBoxLayout()

        scores.setSpacing(12)

        declarer_score = self.create_score_box(
            "DECLARER",
            "0",
            "NEED 10"
        )

        defence_score = self.create_score_box(
            "DEFENCE",
            "0",
            "NEED 4"
        )

        scores.addWidget(declarer_score)
        scores.addWidget(defence_score)

        sidebar_layout.addLayout(
            scores
        )

        # -------------------------------------------------
        # GAME LOG
        # -------------------------------------------------

        log = QFrame()

        log.setObjectName(
            "sidePanel"
        )

        log_layout = QVBoxLayout(log)

        log_layout.setContentsMargins(
            16,
            14,
            16,
            14
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
            1
        )

        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

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
            0
        )

        self.setStyleSheet(
            self.get_style()
        )

    # =====================================================
    # GAME INFORMATION
    # =====================================================

    def update_game_info(self):

        if self.contract_title is None:
            return

        # -------------------------------------------------
        # CONTRACT
        # -------------------------------------------------

        self.contract_title.setText(
            self.contract_text()
        )

        # -------------------------------------------------
        # DECLARER
        # -------------------------------------------------

        if self.declarer_value is not None:

            if self.declarer is None:

                self.declarer_value.setText("—")

            else:

                self.declarer_value.setText(
                    self.position_name(
                        self.declarer
                    )
                )

        # -------------------------------------------------
        # OPENING LEADER
        # -------------------------------------------------

        leader = self.get_leader()

        if self.leader_value is not None:

            if leader is None:

                self.leader_value.setText("—")

            else:

                self.leader_value.setText(
                    self.position_name(
                        leader
                    )
                )

        # -------------------------------------------------
        # TRICK
        # -------------------------------------------------

        if self.trick_value is not None:

            self.trick_value.setText(
                "1 / 13"
            )

        # -------------------------------------------------
        # TRUMP
        # -------------------------------------------------

        if self.contract is not None:

            denomination = self.contract.denomination

            symbol_map = {
                Denomination.CLUBS: "♣",
                Denomination.DIAMONDS: "♦",
                Denomination.HEARTS: "♥",
                Denomination.SPADES: "♠",
                Denomination.NO_TRUMP: "NT",
            }

            if self.trump is not None:

                self.trump.setText(
                    symbol_map.get(
                        denomination,
                        "?"
                    )
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

        # -------------------------------------------------
        # GAME LOG
        # -------------------------------------------------

        if self.game_log is not None:

            dealer_text = (
                self.position_name(self.dealer)
                if self.dealer is not None
                else "—"
            )

            if self.contract is not None:

                contract_text = self.contract_text()

            else:

                contract_text = "No contract"

            leader_text = (
                self.position_name(leader)
                if leader is not None
                else "—"
            )

            self.game_log.setText(
                f"> Cards dealt. {dealer_text[0]} is the dealer "
                f"and bids first.\n\n"
                f"> Bidding complete — {contract_text}.\n\n"
                f"> {leader_text[0] if leader_text != '—' else '—'} "
                f"leads to trick 1."
            )

            self.update_active_player()
    def set_active(self, active):

        self.active = active
        self.update_style()
    def contract_text(self):

        if self.contract is None:

            return "No Contract"

        declarer_letter = (
            self.position_letter(
                self.declarer
            )
            if self.declarer is not None
            else "?"
        )

        return (
            f"{self.contract.level}"
            f"{self.contract.denomination.short}"
            f" by {declarer_letter}"
        )

    # =====================================================
    # PLAYER / POSITION HELPERS
    # =====================================================

    def get_partner(self, position):

        partners = {
            Position.NORTH: Position.SOUTH,
            Position.SOUTH: Position.NORTH,
            Position.EAST: Position.WEST,
            Position.WEST: Position.EAST,
        }

        return partners.get(position)

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

    def get_leader(self):

        if self.declarer is None:

            return None

        # In bridge, the opening lead is made by the
        # player to the left of the declarer.
        order = [
            Position.NORTH,
            Position.EAST,
            Position.SOUTH,
            Position.WEST,
        ]

        index = order.index(
            self.declarer
        )

        return order[
            (index + 3) % 4
        ]

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
            30
        )

        grid.setSpacing(12)

        north = self.trick_slot()
        west = self.trick_slot()
        centre = self.trump_label()
        east = self.trick_slot()
        south = self.trick_slot()

        grid.addWidget(
            north,
            0,
            1
        )

        grid.addWidget(
            west,
            1,
            0
        )

        grid.addWidget(
            centre,
            1,
            1
        )

        grid.addWidget(
            east,
            1,
            2
        )

        grid.addWidget(
            south,
            2,
            1
        )

        return container

    def trick_slot(self):

        slot = QFrame()

        slot.setObjectName(
            "trickSlot"
        )

        slot.setFixedSize(
            70,
            100
        )

        return slot

    def trump_label(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)

        layout.setAlignment(Qt.AlignCenter)

        self.trump = QLabel("NT")
        self.trump.setObjectName("trump")
        self.trump.setAlignment(Qt.AlignCenter)

        self.trump_subtitle = QLabel("TRUMP")
        self.trump_subtitle.setObjectName("trumpSubtitle")
        self.trump_subtitle.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.trump)
        layout.addWidget(self.trump_subtitle)

        return widget

    # =====================================================
    # SIDEBAR HELPERS
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

        row.addWidget(left)
        row.addWidget(right)

        layout.addLayout(row)

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