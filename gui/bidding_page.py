"""
Bidding screen for BridgeTut.
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

from card_model.deck import new_deal
from card_model.player import Position

from .widgets.player_seat import PlayerSeat


class BiddingPage(QWidget):

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

        table.setObjectName("biddingTable")

        table_layout = QGridLayout(table)

        table_layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        table_layout.setSpacing(10)

        # -------------------------------------------------
        # NORTH
        # -------------------------------------------------

        north = PlayerSeat(
            self.players[Position.NORTH],
            role="Dealer",
            active=...,
            hand_orientation="horizontal",
        )
        # -------------------------------------------------
        # EAST
        # -------------------------------------------------

        east = PlayerSeat(
            self.players[Position.EAST],
            hand_orientation="horizontal",
        )

        # -------------------------------------------------
        # SOUTH
        # -------------------------------------------------

        south = PlayerSeat(
                    self.players[Position.SOUTH],
                    role="",
                    active=...,
                    hand_orientation="horizontal",
                )

        # -------------------------------------------------
        # WEST
        # -------------------------------------------------

        west = PlayerSeat(
            self.players[Position.WEST],
            hand_orientation="horizontal",
        )

        table_layout.addWidget(north, 0, 0)
        table_layout.addWidget(east, 0, 1)
        table_layout.addWidget(south, 1, 0)
        table_layout.addWidget(west, 1, 1)

        table_layout.setColumnStretch(0, 1)
        table_layout.setColumnStretch(1, 1)

        table_layout.setRowStretch(0, 1)
        table_layout.setRowStretch(1, 1)

        main_layout.addWidget(table, 1)

        # =================================================
        # RIGHT PANEL
        # =================================================

        right_panel = QWidget()

        right_layout = QVBoxLayout(right_panel)

        right_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        right_layout.setSpacing(14)

        # -------------------------------------------------
        # CONTRACT INFO
        # -------------------------------------------------

        info = QFrame()

        info.setObjectName("infoPanel")

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
            "South"
        )

        self.add_info_row(
            info_layout,
            "VULNERABILITY",
            "Vulnerable"
        )

        self.add_info_row(
            info_layout,
            "TO CALL",
            "South"
        )

        self.add_info_row(
            info_layout,
            "HIGHEST BID",
            "None"
        )

        right_layout.addWidget(info)

        # -------------------------------------------------
        # BIDDING GRID
        # -------------------------------------------------

        bidding_panel = QFrame()

        bidding_panel.setObjectName("biddingPanel")

        bidding_layout = QVBoxLayout(bidding_panel)

        bidding_layout.setContentsMargins(
            16,
            16,
            16,
            14
        )

        bidding_layout.setSpacing(8)

        denominations = [
            "♣",
            "♦",
            "♥",
            "♠",
            "NT",
        ]

        for level in range(1, 8):

            row = QHBoxLayout()

            row.setSpacing(6)

            level_label = QLabel(
                str(level)
            )

            level_label.setFixedWidth(22)

            level_label.setAlignment(
                Qt.AlignCenter
            )

            level_label.setObjectName(
                "levelLabel"
            )

            row.addWidget(level_label)

            for denomination in denominations:

                button = QPushButton(
                    denomination
                )

                button.setObjectName(
                    "bidButton"
                )

                button.setFixedHeight(36)

                row.addWidget(button)

            bidding_layout.addLayout(row)

        # -------------------------------------------------
        # PASS / DOUBLE / REDOUBLE
        # -------------------------------------------------

        calls = QHBoxLayout()

        calls.setSpacing(8)

        pass_button = QPushButton("Pass")

        pass_button.setObjectName(
            "passButton"
        )

        double_button = QPushButton("Double")

        double_button.setObjectName(
            "secondaryButton"
        )

        redouble_button = QPushButton("Redouble")

        redouble_button.setObjectName(
            "secondaryButton"
        )

        calls.addWidget(pass_button)
        calls.addWidget(double_button)
        calls.addWidget(redouble_button)

        bidding_layout.addLayout(calls)

        right_layout.addWidget(
            bidding_panel
        )

        # -------------------------------------------------
        # AUCTION
        # -------------------------------------------------

        auction = QFrame()

        auction.setObjectName(
            "auctionPanel"
        )

        auction_layout = QVBoxLayout(auction)

        auction_layout.setContentsMargins(
            16,
            12,
            16,
            12
        )

        headings = QHBoxLayout()

        for position in ["N", "E", "S", "W"]:

            label = QLabel(position)

            label.setAlignment(
                Qt.AlignCenter
            )

            headings.addWidget(label)

        auction_layout.addLayout(headings)

        line = QFrame()

        line.setFrameShape(
            QFrame.HLine
        )

        line.setObjectName(
            "auctionLine"
        )

        auction_layout.addWidget(line)

        empty = QLabel(
            "No calls yet."
        )

        empty.setAlignment(
            Qt.AlignCenter
        )

        empty.setObjectName(
            "auctionEmpty"
        )

        auction_layout.addWidget(empty)

        right_layout.addWidget(auction)

        main_layout.addWidget(
            right_panel,
            0
        )

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
    ):

        row = QHBoxLayout()

        left = QLabel(label)

        left.setObjectName(
            "infoLabel"
        )

        right = QLabel(value)

        right.setObjectName(
            "infoValue"
        )

        right.setAlignment(
            Qt.AlignRight
        )

        row.addWidget(left)
        row.addWidget(right)

        layout.addLayout(row)

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

        QPushButton#passButton {
            background-color: #51b5ba;
            color: #071710;
            border: none;
            border-radius: 6px;
            padding: 9px;
            font-size: 14px;
            font-weight: bold;
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

        QFrame#auctionLine {
            color: #29483b;
            background-color: #29483b;
            max-height: 1px;
        }

        QLabel#auctionEmpty {
            color: #b9c8c1;
            padding: 10px;
        }

        """