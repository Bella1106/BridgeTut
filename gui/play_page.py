"""
Play screen for BridgeTut.

Day 1 version:
- Displays the four hands.
- Displays the central trick area.
- Displays contract/game information.
- Results button is visual only for now.
"""

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

        self.players = new_deal(
            dealer=Position.SOUTH,
            seed=42,
        )

        self.setup_ui()

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
        # NORTH
        # -------------------------------------------------

        north = PlayerSeat(
            self.players[Position.NORTH],
            role="Defender",
            hand_orientation="horizontal",
        )

        north.setFixedHeight(120)

        # -------------------------------------------------
        # WEST
        # -------------------------------------------------

        west = PlayerSeat(
            self.players[Position.WEST],
            role="Dummy",
            hand_orientation="vertical",
        )

        west.setFixedWidth(155)

        # -------------------------------------------------
        # EAST
        # -------------------------------------------------

        east = PlayerSeat(
            self.players[Position.EAST],
            role="Declarer",
            hand_orientation="vertical",
        )

        east.setFixedWidth(155)

        # -------------------------------------------------
        # SOUTH
        # -------------------------------------------------

        south = PlayerSeat(
            self.players[Position.SOUTH],
            role="Defender",
            active=True,
            hand_orientation="horizontal",
        )

        south.setFixedHeight(120)

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

        contract_title = QLabel(
            "4NT by E"
        )

        contract_title.setObjectName(
            "contractTitle"
        )

        contract_layout.addWidget(
            contract_title
        )

        self.add_side_row(
            contract_layout,
            "DECLARER",
            "East"
        )

        self.add_side_row(
            contract_layout,
            "LEAD / TURN",
            "South"
        )

        self.add_side_row(
            contract_layout,
            "TRICK",
            "1 / 13"
        )

        sidebar_layout.addWidget(
            contract
        )

        # -------------------------------------------------
        # SCORE BOXES
        # -------------------------------------------------

        scores = QHBoxLayout()

        scores.setSpacing(12)

        declarer = self.create_score_box(
            "DECLARER",
            "0",
            "NEED 10"
        )

        defence = self.create_score_box(
            "DEFENCE",
            "0",
            "NEED 4"
        )

        scores.addWidget(declarer)
        scores.addWidget(defence)

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

        messages = QLabel(
            "> Cards dealt. N is the dealer and\n"
            "bids first.\n\n"
            "> Bidding complete — 4NT by E.\n\n"
            "> S leads to trick 1."
        )

        messages.setObjectName(
            "gameLog"
        )

        log_layout.addWidget(
            messages
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

        layout.setAlignment(
            Qt.AlignCenter
        )

        trump = QLabel(
            "NT"
        )

        trump.setObjectName(
            "trump"
        )

        subtitle = QLabel(
            "TRUMP"
        )

        subtitle.setObjectName(
            "trumpSubtitle"
        )

        layout.addWidget(
            trump
        )

        layout.addWidget(
            subtitle
        )

        return widget

    # =====================================================
    # SIDEBAR HELPERS
    # =====================================================

    def add_side_row(
        self,
        layout,
        label,
        value,
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