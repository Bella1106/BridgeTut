from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
)

from .home_page import HomePage
from .bidding_page import BiddingPage
from .play_page import PlayPage
from .placeholder_page import PlaceholderPage

from game_history.history_manager import HistoryManager
from .history_page import HistoryPage

from card_model.player import Position
from game_logic.dealer import determine_next_dealer


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # -------------------------------------------------
        # WINDOW
        # -------------------------------------------------

        self.setWindowTitle(
            "BridgeTut"
        )

        self.resize(
            1248,
            856
        )

        self.setMinimumSize(
            1000,
            700
        )

        # -------------------------------------------------
        # DEALER
        # -------------------------------------------------

        # South is the dealer for the first game.
        # The dealer rotates after each new game.
        self.current_dealer = Position.SOUTH

        # -------------------------------------------------
        # DATA PASSED FROM BIDDING -> PLAY
        # -------------------------------------------------

        self.play_data = None

        # -------------------------------------------------
        # GAME HISTORY
        # -------------------------------------------------

        self.history_manager = HistoryManager()

        # -------------------------------------------------
        # STYLE
        # -------------------------------------------------

        self.setStyleSheet(
            self.get_stylesheet()
        )

        # -------------------------------------------------
        # BUILD UI
        # -------------------------------------------------

        self.setup_ui()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        # -------------------------------------------------
        # CENTRAL WIDGET
        # -------------------------------------------------

        central_widget = QWidget()

        central_widget.setObjectName(
            "centralWidget"
        )

        self.setCentralWidget(
            central_widget
        )

        main_layout = QVBoxLayout(
            central_widget
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(
            0
        )

        # -------------------------------------------------
        # NAVIGATION BAR
        # -------------------------------------------------

        navigation = QWidget()

        navigation.setObjectName(
            "navigationBar"
        )

        nav_layout = QHBoxLayout(
            navigation
        )

        nav_layout.setContentsMargins(
            20,
            0,
            20,
            0
        )

        nav_layout.setSpacing(
            8
        )

        # -------------------------------------------------
        # BRAND
        # -------------------------------------------------

        brand = QLabel(
            "BridgeTut"
        )

        brand.setObjectName(
            "brand"
        )

        nav_layout.addWidget(
            brand
        )

        # -------------------------------------------------
        # PAGE TITLE
        # -------------------------------------------------

        page_title = QLabel(
            "Home"
        )

        page_title.setObjectName(
            "pageTitle"
        )

        nav_layout.addWidget(
            page_title
        )

        nav_layout.addStretch()

        # -------------------------------------------------
        # NAVIGATION BUTTONS
        # -------------------------------------------------

        self.nav_buttons = {}

        pages = [
            "Home",
            "Bidding",
            "Play",
            "Results",
            "History",
        ]

        for name in pages:

            button = QPushButton(
                name
            )

            button.setObjectName(
                "navButton"
            )

            button.setCursor(
                Qt.PointingHandCursor
            )

            button.clicked.connect(
                lambda checked=False,
                page=name:
                self.navigate(page)
            )

            self.nav_buttons[name] = button

            nav_layout.addWidget(
                button
            )

        main_layout.addWidget(
            navigation
        )

        # -------------------------------------------------
        # PAGE STACK
        # -------------------------------------------------

        self.pages = QStackedWidget()

        main_layout.addWidget(
            self.pages
        )

        # =================================================
        # HOME
        # =================================================

        self.home_page = HomePage(
            new_game_callback=lambda:
            self.start_new_game(),

            history_callback=lambda:
            self.navigate("History"),
        )

        self.pages.addWidget(
            self.home_page
        )

        # =================================================
        # DEAL
        # =================================================

        self.deal_page = PlaceholderPage(
            "Deal",
            "Deal screen will be connected to the Deck."
        )

        self.pages.addWidget(
            self.deal_page
        )

        # =================================================
        # BIDDING
        # =================================================

        self.bidding_page = BiddingPage(
            dealer=self.current_dealer
        )

        self.pages.addWidget(
            self.bidding_page
        )

        # =================================================
        # PLAY
        # =================================================

        self.play_page = PlayPage()

        self.pages.addWidget(
            self.play_page
        )

        # =================================================
        # RESULTS
        # =================================================

        self.results_page = PlaceholderPage(
            "Results",
            "Results screen will be connected to scoring."
        )

        self.pages.addWidget(
            self.results_page
        )

        # =================================================
        # HISTORY
        # =================================================

        self.history_page = HistoryPage(
            self.history_manager
        )

        self.pages.addWidget(
            self.history_page
        )

        # -------------------------------------------------
        # STORE PAGE TITLE
        # -------------------------------------------------

        self.page_title = page_title

        # -------------------------------------------------
        # CONNECT PLAY -> RESULTS
        # -------------------------------------------------

        self.play_page.results_button_clicked.connect(
            lambda:
            self.navigate("Results")
        )

        # -------------------------------------------------
        # START ON HOME
        # -------------------------------------------------

        self.navigate(
            "Home"
        )

    # =====================================================
    # NEW GAME
    # =====================================================

    def start_new_game(self):

        # -------------------------------------------------
        # Reset the existing PlayPage completely
        # -------------------------------------------------

        self.play_page.reset_for_new_game()

        # -------------------------------------------------
        # Rotate dealer
        # -------------------------------------------------

        self.current_dealer = determine_next_dealer(
            self.current_dealer
        )

        # -------------------------------------------------
        # Replace the existing BiddingPage
        # -------------------------------------------------

        old_bidding_page = self.bidding_page

        self.bidding_page = BiddingPage(
            dealer=self.current_dealer
        )

        # Replace the existing bidding page at index 2.
        self.pages.insertWidget(
            2,
            self.bidding_page
        )

        self.pages.removeWidget(
            old_bidding_page
        )

        old_bidding_page.deleteLater()

        # -------------------------------------------------
        # Reset play data
        # -------------------------------------------------

        self.play_data = None

        # -------------------------------------------------
        # Go to bidding
        # -------------------------------------------------

        self.navigate(
            "Bidding"
        )

    # =====================================================
    # NAVIGATION
    # =====================================================

    def navigate(
        self,
        page_name
    ):

        page_indexes = {
            "Home": 0,
            "Deal": 1,
            "Bidding": 2,
            "Play": 3,
            "Results": 4,
            "History": 5,
        }

        if page_name not in page_indexes:
            return

        self.pages.setCurrentIndex(
            page_indexes[page_name]
        )

        self.page_title.setText(
            page_name
        )

        # -------------------------------------------------
        # ACTIVE NAVIGATION BUTTON
        # -------------------------------------------------

        for name, button in self.nav_buttons.items():

            button.setProperty(
                "active",
                name == page_name
            )

            button.style().unpolish(
                button
            )

            button.style().polish(
                button
            )

        # -------------------------------------------------
        # PLAY
        # -------------------------------------------------

        if page_name == "Play":

            self.play_page.load_game()

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        if page_name == "History":

            self.history_page.refresh_history()

    # =====================================================
    # APPLICATION STYLE
    # =====================================================

    @staticmethod
    def get_stylesheet():

        return """

        /* =================================================
           GLOBAL
        ================================================= */

        * {
            font-family: "Segoe UI", Arial, sans-serif;
        }

        QMainWindow {
            background-color: #071710;
        }

        QWidget#centralWidget {
            background-color: #071710;
        }

        /* =================================================
           NAVIGATION BAR
        ================================================= */

        QWidget#navigationBar {

            background-color: #11271d;

            border-bottom: 1px solid #294238;

            min-height: 62px;
            max-height: 62px;
        }

        /* =================================================
           BRIDGETUT LOGO
        ================================================= */

        QLabel#brand {

            color: #e5c557;

            font-family: Georgia, serif;

            font-size: 21px;

            font-weight: bold;
        }

        /* =================================================
           CURRENT PAGE TITLE
        ================================================= */

        QLabel#pageTitle {

            color: #f1f4f2;

            font-size: 17px;

            font-weight: bold;

            padding-left: 4px;
        }

        /* =================================================
           NAVIGATION BUTTONS
        ================================================= */

        QPushButton#navButton {

            background-color: transparent;

            color: #c7d2cc;

            border: none;

            border-radius: 6px;

            padding: 9px 14px;

            font-size: 14px;
        }

        QPushButton#navButton:hover {

            background-color: #1b3b2d;

            color: white;
        }

        QPushButton#navButton[active="true"] {

            background-color: #51b5ba;

            color: #071710;

            font-weight: bold;
        }

        /* =================================================
           GENERAL LABELS
        ================================================= */

        QLabel {
            color: #f1f4f2;
        }

        /* =================================================
           SCROLL BAR
        ================================================= */

        QScrollBar:vertical {

            background: #071710;

            width: 10px;
        }

        QScrollBar::handle:vertical {

            background: #29483b;

            border-radius: 5px;
        }

        """