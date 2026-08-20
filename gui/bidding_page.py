#Creates the actual bidding screen, using the new_deal() function.

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
)

from card_model.deck import new_deal
from card_model.player import Position

from .widgets.player_seat import PlayerSeat


class BiddingPage(QWidget):

    def __init__(self):
        super().__init__()

        self.dealer = Position.NORTH

        self.players = new_deal(
            self.dealer
        )

        self.current_player = self.dealer

        self.setup_ui()

    def setup_ui(self):

        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(
            16,
            16,
            16,
            16
        )

        main_layout.setSpacing(16)

        # -------------------------------------------------
        # LEFT: BRIDGE TABLE
        # -------------------------------------------------

        table = QFrame()

        table.setObjectName("bridgeTable")

        table_layout = QGridLayout(table)

        table_layout.setContentsMargins(
            16,
            16,
            16,
            16
        )

        table_layout.setHorizontalSpacing(12)
        table_layout.setVerticalSpacing(12)

        # North

        north = PlayerSeat(
            self.players[Position.NORTH],
            role="Dealer",
            active=self.current_player == Position.NORTH,
        )

        table_layout.addWidget(
            north,
            0,
            1
        )

        # West

        west = PlayerSeat(
            self.players[Position.WEST],
            role="",
            active=self.current_player == Position.WEST,
        )

        table_layout.addWidget(
            west,
            1,
            0
        )

        # East

        east = PlayerSeat(
            self.players[Position.EAST],
            role="",
            active=self.current_player == Position.EAST,
        )

        table_layout.addWidget(
            east,
            1,
            2
        )

        # South

        south = PlayerSeat(
            self.players[Position.SOUTH],
            role="",
            active=self.current_player == Position.SOUTH,
        )

        table_layout.addWidget(
            south,
            2,
            1
        )

        table_layout.setRowStretch(1, 1)
        table_layout.setColumnStretch(1, 1)

        main_layout.addWidget(
            table,
            stretch=3
        )

        # -------------------------------------------------
        # RIGHT SIDEBAR
        # -------------------------------------------------

        sidebar = QVBoxLayout()

        sidebar.setSpacing(16)

        # Game information

        info = self.create_info_panel()

        sidebar.addWidget(info)

        # Bidding controls

        bids = self.create_bid_panel()

        sidebar.addWidget(
            bids,
            stretch=1
        )

        # Auction

        auction = self.create_auction_panel()

        sidebar.addWidget(auction)

        main_layout.addLayout(
            sidebar,
            stretch=1
        )

        self.setStyleSheet("""
            QFrame#bridgeTable {
                background-color: #00602e;
                border-radius: 12px;
            }

            QFrame.panel {
                background-color: #13271e;
                border: 1px solid #29483b;
                border-radius: 10px;
            }

            QLabel.infoLabel {
                color: #b9c5bf;
                font-size: 12px;
                letter-spacing: 1px;
            }

            QLabel.infoValue {
                color: white;
                font-size: 13px;
                font-weight: bold;
            }

            QLabel.sectionTitle {
                color: #e5c557;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton.bidButton {
                background-color: #f3f3ed;
                color: #111111;

                border: none;
                border-radius: 5px;

                min-height: 34px;

                font-size: 14px;
                font-weight: bold;
            }

            QPushButton.bidButton:hover {
                background-color: #e5c557;
            }

            QPushButton.passButton {
                background-color: #51b5ba;
                color: #071710;

                border: none;
                border-radius: 6px;

                min-height: 44px;

                font-size: 15px;
                font-weight: bold;
            }

            QPushButton.passButton:hover {
                background-color: #6bc7ca;
            }

            QLabel.levelLabel {
                color: #c7d1cc;
                font-size: 13px;
            }

            QLabel.auctionPlayer {
                color: #aab8b1;
                font-size: 12px;
            }
        """)

    # -----------------------------------------------------
    # GAME INFORMATION
    # -----------------------------------------------------

    def create_info_panel(self):

        panel = QFrame()
        panel.setProperty("class", "panel")

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(
            16,
            12,
            16,
            12
        )

        self.add_info_row(
            layout,
            "DEALER",
            self.dealer.value
        )

        self.add_info_row(
            layout,
            "VULNERABILITY",
            "Not vulnerable"
        )

        self.add_info_row(
            layout,
            "TO CALL",
            self.current_player.value
        )

        self.add_info_row(
            layout,
            "HIGHEST BID",
            "None"
        )

        return panel

    def add_info_row(
        self,
        layout,
        label,
        value
    ):

        row = QHBoxLayout()

        label_widget = QLabel(label)

        label_widget.setProperty(
            "class",
            "infoLabel"
        )

        value_widget = QLabel(value)

        value_widget.setProperty(
            "class",
            "infoValue"
        )

        row.addWidget(label_widget)

        row.addStretch()

        row.addWidget(value_widget)

        layout.addLayout(row)

    # -----------------------------------------------------
    # BIDDING PANEL
    # -----------------------------------------------------

    def create_bid_panel(self):

        panel = QFrame()
        panel.setProperty("class", "panel")

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        layout.setSpacing(7)

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

            level_label.setProperty(
                "class",
                "levelLabel"
            )

            level_label.setFixedWidth(30)

            level_label.setAlignment(
                Qt.AlignCenter
            )

            row.addWidget(level_label)

            for denomination in denominations:

                button = QPushButton(
                    denomination
                )

                button.setObjectName(
                    "bidButton"
                )

                button.setProperty(
                    "class",
                    "bidButton"
                )

                button.setCursor(
                    Qt.PointingHandCursor
                )

                row.addWidget(button)

            layout.addLayout(row)

        layout.addSpacing(5)

        pass_button = QPushButton("Pass")

        pass_button.setProperty(
            "class",
            "passButton"
        )

        pass_button.setCursor(
            Qt.PointingHandCursor
        )

        layout.addWidget(pass_button)

        return panel

    # -----------------------------------------------------
    # AUCTION PANEL
    # -----------------------------------------------------

    def create_auction_panel(self):

        panel = QFrame()
        panel.setProperty("class", "panel")

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        header = QHBoxLayout()

        for position in [
            "N",
            "E",
            "S",
            "W"
        ]:

            label = QLabel(position)

            label.setProperty(
                "class",
                "auctionPlayer"
            )

            label.setAlignment(
                Qt.AlignCenter
            )

            header.addWidget(label)

        layout.addLayout(header)

        line = QFrame()

        line.setFrameShape(
            QFrame.HLine
        )

        line.setStyleSheet(
            "color: #29483b;"
        )

        layout.addWidget(line)

        empty = QLabel(
            "No calls yet."
        )

        empty.setAlignment(
            Qt.AlignCenter
        )

        empty.setStyleSheet("""
            color: #aebbb5;
            padding: 10px;
        """)

        layout.addWidget(empty)

        return panel