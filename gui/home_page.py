# Code for Home Page

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
)


class HomePage(QWidget):

    def __init__(self, new_game_callback=None):
        super().__init__()

        self.new_game_callback = new_game_callback

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            32,
            28,
            32,
            32
        )

        main_layout.setSpacing(25)

        # -------------------------------------------------
        # GREEN BACKGROUND
        # -------------------------------------------------

        table = QFrame()
        table.setObjectName("homeTable")

        table_layout = QVBoxLayout(table)

        table_layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        table_layout.setSpacing(30)

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title_container = QWidget()

        title_layout = QVBoxLayout(title_container)

        title_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("BridgeTut")
        title.setObjectName("homeTitle")

        subtitle = QLabel(
            "Single-player Contract Bridge — "
            "you play North, East, South and West."
        )

        subtitle.setObjectName("homeSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        table_layout.addStretch()
        table_layout.addWidget(title_container)

        # -------------------------------------------------
        # BUTTON GRID
        # -------------------------------------------------

        cards = QWidget()

        grid = QGridLayout(cards)

        grid.setSpacing(16)

        # New Game

        new_game = self.create_home_card(
            "▷",
            "New Game",
            "Shuffle, deal and take all four seats.",
            selected=True,
        )

        if self.new_game_callback:
            new_game.clicked.connect(self.new_game_callback)

        grid.addWidget(new_game, 0, 0)

        # Load Game

        load_game = self.create_home_card(
            "□",
            "Load Game",
            "0 saved hands.",
        )

        load_game.setEnabled(False)

        grid.addWidget(load_game, 0, 1)

        # Game History

        history = self.create_home_card(
            "↶",
            "Game History",
            "Contracts, results and scores.",
        )

        history.setEnabled(False)

        grid.addWidget(history, 1, 0)

        # Exit

        exit_button = self.create_home_card(
            "→",
            "Exit",
            "Close the table.",
        )

        exit_button.clicked.connect(self.close_application)

        grid.addWidget(exit_button, 1, 1)

        table_layout.addWidget(cards)

        table_layout.addStretch()

        main_layout.addWidget(table)

        # -------------------------------------------------
        # STYLES
        # -------------------------------------------------

        self.setStyleSheet("""

        QFrame#homeTable {
            background-color: #00602e;
            border-radius: 12px;
        }

        QLabel#homeTitle {
            color: #e5c557;
            font-family: Georgia, serif;
            font-size: 44px;
            font-weight: bold;
        }

        QLabel#homeSubtitle {
            color: #d9ebe3;
            font-size: 17px;
            padding-top: 4px;
        }

        QPushButton.homeCard {
            background-color: #172c23;
            border: 1px solid transparent;
            border-radius: 10px;

            color: white;

            text-align: left;
            padding: 18px;
        }

        QPushButton.homeCard:hover {
            border: 1px solid #e5c557;
        }

        QPushButton.homeCard[selected="true"] {
            border: 1px solid #e5c557;
        }

        QPushButton.homeCard:disabled {
            color: #777f7b;
        }

        QLabel.homeIcon {
            color: #e5c557;
            font-size: 28px;
        }

        QLabel.homeCardTitle {
            color: white;
            font-size: 18px;
            font-weight: bold;
        }

        QLabel.homeCardDescription {
            color: #aebbb5;
            font-size: 13px;
        }

        """)

    def create_home_card(
        self,
        icon,
        title,
        description,
        selected=False,
    ):

        button = QPushButton()

        button.setObjectName("homeCard")

        button.setProperty(
            "selected",
            selected
        )

        button.setMinimumHeight(92)

        button.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(button)

        layout.setContentsMargins(
            15,
            12,
            15,
            12
        )

        layout.setSpacing(15)

        icon_label = QLabel(icon)

        icon_label.setProperty(
            "class",
            "homeIcon"
        )

        icon_label.setStyleSheet(
            "color: #e5c557; font-size: 28px;"
        )

        icon_label.setFixedWidth(35)

        layout.addWidget(icon_label)

        text_container = QWidget()

        text_layout = QVBoxLayout(text_container)

        text_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)

        title_label.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)

        description_label = QLabel(description)

        description_label.setStyleSheet("""
            color: #aebbb5;
            font-size: 13px;
        """)

        text_layout.addWidget(title_label)
        text_layout.addWidget(description_label)

        layout.addWidget(text_container)

        return button

    def close_application(self):

        from PySide6.QtWidgets import QApplication

        QApplication.quit()