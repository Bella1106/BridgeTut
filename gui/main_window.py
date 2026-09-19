from pathlib import Path
from copy import deepcopy

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

from .placeholder_page import PlaceholderPage
from .home_page import HomePage
from .bidding_page import BiddingPage
from .play_page import PlayPage
from .history_page import HistoryPage

from game_history.history_manager import HistoryManager
from card_model.deck import deal_from
from card_model.player import Position
from game_logic.dealer import determine_next_dealer
from game_logic.lesson import LessonState
from game_logic.tutorial_parser import parse_bid_and_play_lessons
from game_logic.tutorial_play import build_mode_one_lesson
from game_logic.guided_bidding import (
    GuidedBiddingState,
    GuidedBiddingLesson,
)
from game_logic.tutorial_bbo_examples import (
    get_bbo_tutorials,
    load_bbo_tutorial,
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

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

        self.current_dealer = Position.SOUTH

        self.board_number = 1

        self.play_data = None

        self.history_manager = HistoryManager()

        self.setStyleSheet(
            self.get_stylesheet()
        )

        self.setup_ui()

    # =====================================================
    # UI SETUP
    # =====================================================

    def setup_ui(self):

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

        brand = QLabel(
            "BridgeTut"
        )

        brand.setObjectName(
            "brand"
        )

        nav_layout.addWidget(
            brand
        )

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

            resume_game_callback=lambda:
            self.resume_game(),

            should_show_resume_callback=lambda:
            self.has_unfinished_game(),

            history_callback=lambda:
            self.navigate("History"),

            lesson_callback=lambda mode:
            self.handle_lesson_selection(mode),

            tutorials_callback=lambda mode, filename:
            self.start_bbo_example(filename)
            if mode == "bbo"
            else None,
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
            self.history_manager,
            play_deal_callback=lambda game:
            self.play_existing_deal(game),
        )

        self.pages.addWidget(
            self.history_page
        )

        self.page_title = page_title

        self.navigate(
            "Home"
        )

    # =====================================================
    # UNFINISHED GAME CHECK
    # =====================================================

    def has_unfinished_game(self):

        latest_game = (
            self.history_manager.get_latest_game()
        )

        if latest_game is None:

            return False

        return not latest_game.is_complete

    # =====================================================
    # RESUME GAME
    # =====================================================

    def resume_game(self):

        latest_game = (
            self.history_manager.get_latest_game()
        )

        # -------------------------------------------------
        # Safety fallback
        # -------------------------------------------------

        if latest_game is None:

            self.start_new_game()

            return

        # -------------------------------------------------
        # A completed latest game cannot be resumed.
        # -------------------------------------------------

        if latest_game.is_complete:

            self.start_new_game()

            return

        # -------------------------------------------------
        # If PlayPage is already displaying this exact
        # GameRecord, do NOT reset it.
        #
        # This preserves partial-trick state.
        # -------------------------------------------------

        if (
            self.play_page.game_loaded
            and self.play_page.game_record
            is latest_game
        ):

            self.play_data = {
                "resume_game_record": latest_game,
            }

            self.navigate(
                "Play"
            )

            return

        # -------------------------------------------------
        # Otherwise load the saved GameRecord.
        # -------------------------------------------------

        self.play_page.reset_for_new_game()

        self.play_data = {
            "resume_game_record": latest_game,
        }

        self.navigate(
            "Play"
        )

    # =====================================================
    # PLAY EXISTING DEAL
    # =====================================================

    def play_existing_deal(
        self,
        game,
    ):

        if game is None:

            return

        # -------------------------------------------------
        # COPY THE ORIGINAL PLAYERS/HANDS
        #
        # The historical game must not be modified when
        # the replay is played.
        # -------------------------------------------------

        players = deepcopy(
            game.players
        )

        # -------------------------------------------------
        # Reset the currently loaded play game.
        # -------------------------------------------------

        self.play_page.reset_for_new_game()

        # -------------------------------------------------
        # Create a fresh BiddingPage using the exact
        # same deal.
        # -------------------------------------------------

        old_bidding_page = self.bidding_page

        self.bidding_page = BiddingPage(
            dealer=game.dealer,
            board_number=game.board_number,
            players=players,
        )

        self.pages.insertWidget(
            1,
            self.bidding_page
        )

        self.pages.removeWidget(
            old_bidding_page
        )

        old_bidding_page.deleteLater()

        # -------------------------------------------------
        # This is a new game.
        #
        # BiddingPage will create the appropriate
        # play_data when the auction finishes.
        # -------------------------------------------------

        self.play_data = None

        self.navigate(
            "Bidding"
        )

    # =====================================================
    # START NEW GAME
    # =====================================================

    def start_new_game(self):

        self.play_page.reset_for_new_game()

        self.current_dealer = determine_next_dealer(
            self.current_dealer
        )

        self.board_number += 1

        old_bidding_page = self.bidding_page

        self.bidding_page = BiddingPage(
            dealer=self.current_dealer,
            board_number=self.board_number,
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

    # =====================================================
    # RESTART BIDDING
    # =====================================================

    def restart_bidding(self):

        self.play_page.reset_for_new_game()

        old_bidding_page = self.bidding_page

        # =================================================
        # BBO EXAMPLE
        # =================================================

        if old_bidding_page.bbo_game_data is not None:

            self.bidding_page = BiddingPage(
                bbo_game_data=(
                    old_bidding_page.bbo_game_data
                ),

                players=(
                    old_bidding_page.players
                ),
            )

        # =================================================
        # GUIDED LESSON
        # =================================================

        elif old_bidding_page.tutorial_lesson_data is not None:

            tutorial_data = (
                old_bidding_page.tutorial_lesson_data
            )

            guided_lesson = GuidedBiddingLesson(
                dealer=tutorial_data.dealer,
                script=tutorial_data.auction,
                user_seat=Position.SOUTH,
            )

            guided_state = GuidedBiddingState(
                guided_lesson
            )

            self.bidding_page = BiddingPage(
                guided_bidding_state=guided_state,
                tutorial_lesson_data=tutorial_data,
                players=old_bidding_page.players,
            )

            self.bidding_page.guided_auction_finished.connect(
                self.finish_bid_and_play_lesson
            )

        # =================================================
        # NORMAL GAME
        # =================================================

        else:

            self.bidding_page = BiddingPage(
                dealer=old_bidding_page.dealer,
                board_number=old_bidding_page.board_number,
                players=old_bidding_page.players,
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

    # =====================================================
    # BBO EXAMPLE
    # =====================================================

    def start_bbo_example(
        self,
        filename,
    ):

        self.play_page.reset_for_new_game()

        selected_tutorial = None

        for tutorial in get_bbo_tutorials():

            if tutorial.filename == filename:

                selected_tutorial = tutorial

                break

        if selected_tutorial is None:

            return

        bbo_game_data = load_bbo_tutorial(
            selected_tutorial
        )

        old_bidding_page = self.bidding_page

        self.bidding_page = BiddingPage(
            bbo_game_data=bbo_game_data,
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

    # =====================================================
    # BID + PLAY LESSON
    # =====================================================

    def start_bid_and_play_lesson(
        self,
        tutorial_data,
    ):

        self.play_page.reset_for_new_game()

        guided_lesson = GuidedBiddingLesson(
            dealer=tutorial_data.dealer,
            script=tutorial_data.auction,
            user_seat=Position.SOUTH,
        )

        guided_state = GuidedBiddingState(
            guided_lesson
        )

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

    # =====================================================
    # FINISH BID + PLAY LESSON
    # =====================================================

    def finish_bid_and_play_lesson(
        self,
        tutorial_data,
    ):

        lesson = build_mode_one_lesson(
            tutorial_data
        )

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
    # START LESSON
    # =====================================================

    def start_lesson(self):

        self.play_page.reset_for_new_game()

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
    # LESSON SELECTION
    # =====================================================

    def handle_lesson_selection(
        self,
        mode,
    ):

        if mode == "play_only":

            self.start_lesson()

        elif mode == "bid_and_play":

            self.start_bid_and_play()

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

        if page_name == "Play":

            self.play_page.load_game()

        if page_name == "History":

            self.history_page.refresh_history()

    # =====================================================
    # STYLE
    # =====================================================

    @staticmethod
    def get_stylesheet():

        return """

        * {
            font-family: "Segoe UI", Arial, sans-serif;
        }

        QMainWindow {
            background-color: #071710;
        }

        QWidget#centralWidget {
            background-color: #071710;
        }

        QWidget#navigationBar {
            background-color: #11271d;
            border-bottom: 1px solid #294238;
            min-height: 62px;
            max-height: 62px;
        }

        QLabel#brand {
            color: #e5c557;
            font-family: Georgia, serif;
            font-size: 21px;
            font-weight: bold;
        }

        QLabel#pageTitle {
            color: #f1f4f2;
            font-size: 17px;
            font-weight: bold;
            padding-left: 4px;
        }

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

        QLabel {
            color: #f1f4f2;
        }

        QScrollBar:vertical {
            background: #071710;
            width: 10px;
        }

        QScrollBar::handle:vertical {
            background: #29483b;
            border-radius: 5px;
        }

        """

    # =====================================================
    # START TEST MODE ONE
    # =====================================================

    def start_bid_and_play(self):

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