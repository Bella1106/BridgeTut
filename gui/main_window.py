from pathlib import Path

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

from card_model.deck import deal_from
from card_model.player import Position
from game_logic.dealer import determine_next_dealer
from game_logic.lesson import LessonState
from game_logic.tutorial_parser import parse_bid_and_play_lessons
from game_logic.tutorial_play import build_mode_one_lesson
from game_logic.guided_bidding import GuidedBiddingState, GuidedBiddingLesson


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
        # BOARD NUMBER
        # -------------------------------------------------

        # Vulnerability is fixed by the board number, so the
        # boards are counted from 1 and never reset.
        self.board_number = 1

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

            # TODO: Replace temporary Mode 1 launcher once the
            # final lesson-selection GUI is integrated.
            lesson_callback=lambda:
            self.start_test_mode_one(),
        )

        self.pages.addWidget(
            self.home_page
        )

        # =================================================
        # BIDDING
        # =================================================

        self.bidding_page = BiddingPage(
            dealer=self.current_dealer,
            board_number=self.board_number,
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
        # Advance to the next board
        # -------------------------------------------------

        self.board_number += 1

        # -------------------------------------------------
        # Replace the existing BiddingPage
        # -------------------------------------------------

        old_bidding_page = self.bidding_page

        self.bidding_page = BiddingPage(
            dealer=self.current_dealer,
            board_number=self.board_number,
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
    # TUTORIAL LESSON (MODE 1: BID + PLAY)
    # =====================================================

    def start_bid_and_play_lesson(self, tutorial_data):

        # -------------------------------------------------
        # Reset PlayPage
        # -------------------------------------------------

        self.play_page.reset_for_new_game()

        # -------------------------------------------------
        # Build guided bidding state
        # -------------------------------------------------

        guided_lesson = GuidedBiddingLesson(
            dealer=tutorial_data.dealer,
            script=tutorial_data.auction,
            user_seat=Position.SOUTH,
        )

        guided_state = GuidedBiddingState(
            guided_lesson
        )

        # -------------------------------------------------
        # Replace normal BiddingPage with tutorial version
        # -------------------------------------------------

        old_bidding_page = self.bidding_page

        self.bidding_page = BiddingPage(
            guided_bidding_state=guided_state,
            tutorial_lesson_data=tutorial_data,
        )

        self.bidding_page.guided_auction_finished.connect(
            self.finish_bid_and_play_lesson
        )

        self.pages.insertWidget(
            1,
            self.bidding_page
        )

        self.pages.removeWidget(
            old_bidding_page
        )

        old_bidding_page.deleteLater()

        self.play_data = None

        self.navigate(
            "Bidding"
        )


    def finish_bid_and_play_lesson(
        self,
        tutorial_data,
    ):

        # -------------------------------------------------
        # Build prescribed play lesson
        # -------------------------------------------------

        lesson = build_mode_one_lesson(
            tutorial_data
        )

        # -------------------------------------------------
        # Hand lesson to existing PlayPage infrastructure
        # -------------------------------------------------

        self.play_data = {
            "players": deal_from(lesson.hands),
            "dealer": lesson.dealer,
            "board_number": None,
            "contract": lesson.contract,
            "declarer": lesson.contract.declarer,
            "history": list(
                self.bidding_page.bidding_system.history
            ),
            "doubling_state":
                self.bidding_page.bidding_system.doubling_state,
            "lesson_state": LessonState(lesson),
            "lesson_ending": tutorial_data.ending,
            "lesson_note": tutorial_data.note,
        }

        self.navigate(
            "Play"
        )

    # =====================================================
    # PRACTICE LESSON (MODE 2: PLAY ONLY)
    # =====================================================

    def start_lesson(self):

        # -------------------------------------------------
        # Reset the existing PlayPage completely
        # -------------------------------------------------

        self.play_page.reset_for_new_game()

        # -------------------------------------------------
        # Build the lesson
        # -------------------------------------------------

        # PLACEHOLDER: always the first of Sonia's real sponsor
        # lessons, until there's a way to choose between them.

        lessons_file = (
            Path(__file__).resolve().parent.parent
            / "tests"
            / "lessons"
            / "exampleBidAndPlay.txt"
        )

        tutorial_data = parse_bid_and_play_lessons(
            lessons_file.read_text()
        )[0]

        lesson = build_mode_one_lesson(
            tutorial_data
        )

        # -------------------------------------------------
        # Skip bidding entirely -- the lesson already has its
        # contract -- and hand PlayPage its data directly, the
        # same way BiddingPage normally would.
        # -------------------------------------------------

        self.play_data = {
            "players": deal_from(lesson.hands),
            "dealer": lesson.dealer,
            "board_number": None,
            "contract": lesson.contract,
            "declarer": lesson.contract.declarer,
            "history": [],
            "doubling_state": None,
            "lesson_state": LessonState(lesson),
            "lesson_ending": tutorial_data.ending,
            "lesson_note": tutorial_data.note,
        }

        self.navigate(
            "Play"
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
            "Bidding": 1,
            "Play": 2,
            "History": 3,
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

    # TODO: Temporary launcher for testing Mode 1.
    # Remove once lesson selection is wired into the GUI.
    def start_test_mode_one(self):

        lessons_file = (
            Path(__file__).resolve().parent.parent
            / "tests"
            / "lessons"
            / "exampleBidAndPlay.txt"
        )

        tutorial_data = parse_bid_and_play_lessons(
            lessons_file.read_text()
        )[0]

        self.start_bid_and_play_lesson(
            tutorial_data
        )