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

    # =====================================================
    # UI SETUP
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            32,
            28,
            32,
            32
        )

        main_layout.setSpacing(25)

        # =================================================
        # GREEN BACKGROUND
        # =================================================

        table = QFrame()

        table.setObjectName(
            "homeTable"
        )

        table_layout = QVBoxLayout(table)

        table_layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        table_layout.setSpacing(30)

        # =================================================
        # TITLE
        # =================================================

        title_container = QWidget()

        title_layout = QVBoxLayout(
            title_container
        )

        title_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        title_layout.setSpacing(6)

        title_layout.setAlignment(
            Qt.AlignCenter
        )

        title = QLabel(
            "BridgeTut"
        )

        title.setObjectName(
            "homeTitle"
        )

        subtitle = QLabel(
            "Single-player Contract Bridge — "
            "you play North, East, South and West."
        )

        subtitle.setObjectName(
            "homeSubtitle"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        title_layout.addWidget(
            title
        )

        title_layout.addWidget(
            subtitle
        )

        table_layout.addStretch()

        table_layout.addWidget(
            title_container
        )

        # =================================================
        # BUTTON GRID
        # =================================================

        cards = QWidget()

        grid = QGridLayout(
            cards
        )

        grid.setContentsMargins(
            0,
            0,
            0,
            0
        )

        grid.setSpacing(
            16
        )

        # =================================================
        # NEW GAME
        # =================================================

        new_game = self.create_home_card(
            "▷",
            "New Game",
            "Shuffle, deal and take all four seats.",
            selected=True,
        )

        if self.new_game_callback:

            new_game.clicked.connect(
                self.new_game_callback
            )

        grid.addWidget(
            new_game,
            0,
            0
        )

        # =================================================
        # LOAD GAME
        # =================================================

        load_game = self.create_home_card(
            "□",
            "Load Game",
            "Open a previously saved hand.",
        )

        load_game.setEnabled(
            False
        )

        grid.addWidget(
            load_game,
            0,
            1
        )

        # =================================================
        # GAME HISTORY
        # =================================================

        history = self.create_home_card(
            "↶",
            "Game History",
            "View contracts, results and scores.",
        )

        history.setEnabled(
            False
        )

        grid.addWidget(
            history,
            1,
            0
        )

        # =================================================
        # EXIT
        # =================================================

        exit_button = self.create_home_card(
            "→",
            "Exit",
            "Close BridgeTut.",
        )

        exit_button.clicked.connect(
            self.close_application
        )

        grid.addWidget(
            exit_button,
            1,
            1
        )

        table_layout.addWidget(
            cards
        )

        table_layout.addStretch()

        main_layout.addWidget(
            table
        )

        # =================================================
        # STYLES
        # =================================================

        self.setStyleSheet("""

        /* =============================================
           MAIN HOME TABLE
           ============================================= */

        QFrame#homeTable {
            background-color: #00602e;
            border-radius: 12px;
        }


        /* =============================================
           TITLE
           ============================================= */

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


        /* =============================================
           HOME CARDS
           ============================================= */

        QPushButton#homeCard {
            background-color: #11271d;

            border: 1px solid #29483b;
            border-radius: 10px;

            color: #f1f4f2;

            text-align: left;

            padding: 18px;
        }


        /* Hover */

        QPushButton#homeCard:hover {
            background-color: #18382a;
            border: 1px solid #e5c557;
        }


        /* Selected */

        QPushButton#homeCard[selected="true"] {
            background-color: #18382a;
            border: 2px solid #e5c557;
        }


        /* Pressed */

        QPushButton#homeCard:pressed {
            background-color: #0d2118;
        }


        /* Disabled */

        QPushButton#homeCard:disabled {
            background-color: #172c23;
            border: 1px solid #263d33;

            color: #aebbb5;
        }


        /* =============================================
           CARD ICON
           ============================================= */

        QLabel#homeIcon {
            color: #e5c557;
            font-size: 28px;
        }


        /* =============================================
           CARD TITLE
           ============================================= */

        QLabel#homeCardTitle {
            color: #f1f4f2;
            font-size: 18px;
            font-weight: bold;
        }


        /* =============================================
           CARD DESCRIPTION
           ============================================= */

        QLabel#homeCardDescription {
            color: #aebbb5;
            font-size: 13px;
        }

        """)

    # =====================================================
    # CREATE HOME CARD
    # =====================================================

    def create_home_card(
        self,
        icon,
        title,
        description,
        selected=False,
    ):

        button = QPushButton()

        button.setObjectName(
            "homeCard"
        )

        button.setProperty(
            "selected",
            selected
        )

        button.setMinimumHeight(
            92
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        # -------------------------------------------------
        # CARD LAYOUT
        # -------------------------------------------------

        layout = QHBoxLayout(
            button
        )

        layout.setContentsMargins(
            15,
            12,
            15,
            12
        )

        layout.setSpacing(
            15
        )

        # -------------------------------------------------
        # ICON
        # -------------------------------------------------

        icon_label = QLabel(
            icon
        )

        icon_label.setObjectName(
            "homeIcon"
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setFixedWidth(
            35
        )

        layout.addWidget(
            icon_label
        )

        # -------------------------------------------------
        # TEXT CONTAINER
        # -------------------------------------------------

        text_container = QWidget()

        text_layout = QVBoxLayout(
            text_container
        )

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        text_layout.setSpacing(
            3
        )

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "homeCardTitle"
        )

        # -------------------------------------------------
        # DESCRIPTION
        # -------------------------------------------------

        description_label = QLabel(
            description
        )

        description_label.setObjectName(
            "homeCardDescription"
        )

        description_label.setWordWrap(
            True
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            description_label
        )

        layout.addWidget(
            text_container
        )

        return button

    # =====================================================
    # EXIT
    # =====================================================

    def close_application(self):

        QApplication.quit()