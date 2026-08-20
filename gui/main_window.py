"""
Main application window for BridgeTut.

This module controls the main desktop window and navigation
between the different sections of the application.
"""

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
from .placeholder_page import PlaceholderPage


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # -------------------------------------------------
        # WINDOW
        # -------------------------------------------------

        self.setWindowTitle("BridgeTut")

        # Target size based on the reference GUI
        self.resize(1248, 856)

        # Prevent the window from becoming smaller than
        # the layouts can comfortably support.
        self.setMinimumSize(1000, 700)

        self.setStyleSheet(self.get_stylesheet())

        self.setup_ui()

    def setup_ui(self):

        # -------------------------------------------------
        # CENTRAL WIDGET
        # -------------------------------------------------

        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")

        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.setSpacing(0)

        # -------------------------------------------------
        # NAVIGATION BAR
        # -------------------------------------------------

        navigation = QWidget()
        navigation.setObjectName("navigationBar")

        nav_layout = QHBoxLayout(navigation)

        nav_layout.setContentsMargins(
            20,
            0,
            20,
            0
        )

        nav_layout.setSpacing(8)

        # -------------------------------------------------
        # BRAND
        # -------------------------------------------------

        brand = QLabel("BridgeTut")
        brand.setObjectName("brand")

        nav_layout.addWidget(brand)

        # -------------------------------------------------
        # PAGE TITLE
        # -------------------------------------------------

        page_title = QLabel("Home")
        page_title.setObjectName("pageTitle")

        nav_layout.addWidget(page_title)

        # Push navigation buttons to the right
        nav_layout.addStretch()

        # -------------------------------------------------
        # NAVIGATION BUTTONS
        # -------------------------------------------------

        self.nav_buttons = {}

        pages = [
            "Home",
            "Deal",
            "Bidding",
            "Play",
            "Results",
            "History",
        ]

        for name in pages:

            button = QPushButton(name)

            button.setObjectName("navButton")

            button.setCursor(
                Qt.PointingHandCursor
            )

            # Capture the current page name
            button.clicked.connect(
                lambda checked=False, page=name:
                self.navigate(page)
            )

            self.nav_buttons[name] = button

            nav_layout.addWidget(button)

        main_layout.addWidget(navigation)

        # -------------------------------------------------
        # PAGE STACK
        # -------------------------------------------------

        self.pages = QStackedWidget()

        main_layout.addWidget(self.pages)

        # -------------------------------------------------
        # HOME
        # -------------------------------------------------

        self.home_page = HomePage(
            new_game_callback=lambda:
            self.navigate("Bidding")
        )

        self.pages.addWidget(
            self.home_page
        )

        # -------------------------------------------------
        # DEAL
        # -------------------------------------------------

        self.deal_page = PlaceholderPage(
            "Deal",
            "Deal screen will be connected to the Deck."
        )

        self.pages.addWidget(
            self.deal_page
        )

        # -------------------------------------------------
        # BIDDING
        # -------------------------------------------------

        self.bidding_page = BiddingPage()

        self.pages.addWidget(
            self.bidding_page
        )

        # -------------------------------------------------
        # PLAY
        # -------------------------------------------------

        self.play_page = PlaceholderPage(
            "Play",
            "Play screen will be connected to the game logic."
        )

        self.pages.addWidget(
            self.play_page
        )

        # -------------------------------------------------
        # RESULTS
        # -------------------------------------------------

        self.results_page = PlaceholderPage(
            "Results",
            "Results screen will be connected to scoring."
        )

        self.pages.addWidget(
            self.results_page
        )

        # -------------------------------------------------
        # HISTORY
        # -------------------------------------------------

        self.history_page = PlaceholderPage(
            "History",
            "Game history will appear here."
        )

        self.pages.addWidget(
            self.history_page
        )

        # Save reference to page title
        self.page_title = page_title

        # Start on Home
        self.navigate("Home")

    # =====================================================
    # NAVIGATION
    # =====================================================

    def navigate(self, page_name):

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

        # Change page
        self.pages.setCurrentIndex(
            page_indexes[page_name]
        )

        # Change title
        self.page_title.setText(
            page_name
        )

        # Update active navigation button
        for name, button in self.nav_buttons.items():

            button.setProperty(
                "active",
                name == page_name
            )

            # Force stylesheet refresh
            button.style().unpolish(button)
            button.style().polish(button)

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