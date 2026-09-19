import tempfile
import unittest
from pathlib import Path

import pytest

from PySide6.QtWidgets import QApplication, QLabel

from gui.main_window import MainWindow
from gui.bidding_page import BiddingPage
from gui.play_page import PlayPage
from gui.history_page import HistoryPage
from gui.widgets.card_widget import CardWidget
from gui.widgets.player_seat import PlayerSeat

from card_model.player import Position
from card_model.deck import new_deal

from game_history.history_manager import HistoryManager


# =========================================================
# QT FIXTURE
# =========================================================

@pytest.fixture
def app():
    """
    Create a QApplication for the GUI tests.

    QApplication.instance() prevents creating more than
    one QApplication during the test session.
    """
    application = QApplication.instance()

    if application is None:
        application = QApplication([])

    return application


# =========================================================
# MAIN WINDOW FIXTURE
# =========================================================

@pytest.fixture
def main_window(app):
    """
    Create a fresh MainWindow for each test.

    The application's real history.pkl file is replaced with
    a temporary history file so GUI tests cannot load or
    modify real saved games.
    """

    temp_directory = tempfile.TemporaryDirectory()

    original_history_file = HistoryManager.HISTORY_FILE

    HistoryManager.HISTORY_FILE = (
        Path(temp_directory.name) / "history.pkl"
    )

    window = MainWindow()

    yield window

    window.close()

    HistoryManager.HISTORY_FILE = original_history_file

    temp_directory.cleanup()


# =========================================================
# MAIN WINDOW
# =========================================================

def test_main_window_launches(main_window):
    """
    Test that the main BridgeTut window launches correctly.
    """

    assert main_window is not None

    assert main_window.windowTitle() == "BridgeTut"

    assert main_window.width() >= 1000
    assert main_window.height() >= 700


def test_main_window_has_page_stack(main_window):
    """
    Test that the main window contains all current
    application pages.

    Current pages:

        1. Home
        2. Bidding
        3. Play
        4. History
    """

    assert main_window.pages is not None

    assert main_window.pages.count() == 4

    assert main_window.pages.widget(0) == (
        main_window.home_page
    )

    assert main_window.pages.widget(1) == (
        main_window.bidding_page
    )

    assert main_window.pages.widget(2) == (
        main_window.play_page
    )

    assert main_window.pages.widget(3) == (
        main_window.history_page
    )


def test_navigation_buttons_exist(main_window):
    """
    Test that all current main navigation buttons are present.
    """

    expected_buttons = [
        "Home",
        "Bidding",
        "Play",
        "History",
    ]

    assert len(main_window.nav_buttons) == 4

    for name in expected_buttons:

        assert name in main_window.nav_buttons

        assert main_window.nav_buttons[name] is not None


def test_home_is_initial_page(main_window):
    """
    The application should start on the Home page.
    """

    assert (
        main_window.pages.currentWidget()
        == main_window.home_page
    )

    assert main_window.page_title.text() == "Home"


# =========================================================
# NAVIGATION
# =========================================================

def test_can_navigate_to_bidding(main_window):
    """
    Test that the Bidding page can be selected.
    """

    main_window.navigate("Bidding")

    assert (
        main_window.pages.currentWidget()
        == main_window.bidding_page
    )

    assert main_window.page_title.text() == "Bidding"


def test_can_navigate_to_play(main_window):
    """
    Test that the Play page can be selected.
    """

    main_window.navigate("Play")

    assert (
        main_window.pages.currentWidget()
        == main_window.play_page
    )

    assert main_window.page_title.text() == "Play"


def test_can_navigate_to_history(main_window):
    """
    Test that the History page can be selected.
    """

    main_window.navigate("History")

    assert (
        main_window.pages.currentWidget()
        == main_window.history_page
    )

    assert main_window.page_title.text() == "History"


def test_invalid_navigation_does_nothing(main_window):
    """
    Invalid page names should not change the current page.
    """

    main_window.navigate("Home")

    current_page = main_window.pages.currentWidget()

    main_window.navigate("NotARealPage")

    assert (
        main_window.pages.currentWidget()
        == current_page
    )

    assert main_window.page_title.text() == "Home"


def test_navigation_through_all_pages(main_window):
    """
    Test that all current application pages can be reached.
    """

    pages = [
        ("Home", main_window.home_page),
        ("Bidding", main_window.bidding_page),
        ("Play", main_window.play_page),
        ("History", main_window.history_page),
    ]

    for page_name, expected_page in pages:

        main_window.navigate(page_name)

        assert (
            main_window.pages.currentWidget()
            == expected_page
        )

        assert (
            main_window.page_title.text()
            == page_name
        )


# =========================================================
# PAGE OBJECTS
# =========================================================

def test_history_page_can_be_created(main_window):
    """
    Test that the HistoryPage exists and is connected to
    the application's history manager.
    """

    assert main_window.history_page is not None

    assert isinstance(
        main_window.history_page,
        HistoryPage,
    )

    assert (
        main_window.history_page.history_manager
        == main_window.history_manager
    )


# =========================================================
# BIDDING PAGE
# =========================================================

def test_bidding_page_can_be_created(app):
    """
    Test that the BiddingPage can be created successfully.
    """

    page = BiddingPage()

    assert page is not None

    page.close()


def test_bidding_page_has_players(app):
    """
    The BiddingPage should create a deal and have four
    player positions available.
    """

    page = BiddingPage()

    assert page.players is not None

    assert Position.NORTH in page.players
    assert Position.SOUTH in page.players
    assert Position.EAST in page.players
    assert Position.WEST in page.players

    page.close()


def test_bidding_page_has_bidding_system(app):
    """
    The GUI should contain the existing BiddingSystem
    rather than implementing a separate bidding engine.
    """

    page = BiddingPage()

    assert page.bidding_system is not None

    page.close()


def test_bidding_page_has_player_seats(app):
    """
    Test that the four player seats are created.
    """

    page = BiddingPage()

    assert len(page.player_seats) == 4

    assert Position.NORTH in page.player_seats
    assert Position.SOUTH in page.player_seats
    assert Position.EAST in page.player_seats
    assert Position.WEST in page.player_seats

    page.close()


# =========================================================
# PLAY PAGE
# =========================================================

def test_play_page_can_be_created(app):
    """
    Test that the PlayPage can be instantiated.
    """

    page = PlayPage()

    assert page is not None

    page.close()


def test_play_page_initial_state(app):
    """
    Before a game is loaded, PlayPage should not have
    game data loaded.
    """

    page = PlayPage()

    assert page.players is None
    assert page.contract is None
    assert page.declarer is None
    assert page.game_complete is False
    assert page.trick_number == 1

    page.close()


# =========================================================
# CARD WIDGET
# =========================================================

def test_card_widget_can_be_created(app):
    """
    Use a card from the GUI's own generated deal so that
    this test does not depend on guessing the Card
    constructor.

    Hand does not support direct indexing, so the first
    sorted card is used.
    """

    bidding_page = BiddingPage()

    card = bidding_page.players[
        Position.SOUTH
    ].hand.sorted_by_suit()[0]

    widget = CardWidget(card)

    assert widget is not None

    assert widget.card == card

    widget.close()
    bidding_page.close()


def test_card_widget_displays_card(app):
    """
    Test that CardWidget displays the card's rank and suit.
    """

    bidding_page = BiddingPage()

    card = bidding_page.players[
        Position.SOUTH
    ].hand.sorted_by_suit()[0]

    widget = CardWidget(card)

    expected_text = (
        f"{card.rank.short}"
        f"{card.suit.symbol}"
    )

    assert widget.top_label.text() == expected_text
    assert widget.bottom_label.text() == expected_text

    widget.close()
    bidding_page.close()


def test_card_widget_starts_unselected(app):
    """
    A card should initially not be selected.
    """

    bidding_page = BiddingPage()

    card = bidding_page.players[
        Position.SOUTH
    ].hand.sorted_by_suit()[0]

    widget = CardWidget(card)

    assert widget.selected is False

    widget.close()
    bidding_page.close()


def test_card_widget_selection_changes(app):
    """
    Test the CardWidget's selection behaviour.
    """

    bidding_page = BiddingPage()

    card = bidding_page.players[
        Position.SOUTH
    ].hand.sorted_by_suit()[0]

    widget = CardWidget(card)

    assert widget.selected is False

    widget.toggle_selected()

    assert widget.selected is True

    widget.toggle_selected()

    assert widget.selected is False

    widget.close()
    bidding_page.close()


# =========================================================
# PLAYER SEAT
# =========================================================

def test_player_seat_can_be_created(app):
    """
    Test that a PlayerSeat can be created using a player
    from the existing card model.
    """

    bidding_page = BiddingPage()

    player = bidding_page.players[
        Position.SOUTH
    ]

    seat = PlayerSeat(
        player,
        role="Dealer",
        active=False,
        dealer=False,
    )

    assert seat is not None
    assert seat.player == player

    seat.close()
    bidding_page.close()


def test_player_seat_displays_player_position(app):
    """
    Test that the player's position is displayed.
    """

    bidding_page = BiddingPage()

    player = bidding_page.players[
        Position.SOUTH
    ]

    seat = PlayerSeat(
        player,
        role="Dealer",
    )

    labels = seat.findChildren(QLabel)

    texts = [
        label.text()
        for label in labels
    ]

    assert player.position.value in texts

    seat.close()
    bidding_page.close()


def test_player_seat_starts_inactive(app):
    """
    Test the initial active state.
    """

    bidding_page = BiddingPage()

    player = bidding_page.players[
        Position.SOUTH
    ]

    seat = PlayerSeat(
        player,
        active=False,
    )

    assert seat.active is False

    seat.set_active(False)

    seat.close()
    bidding_page.close()


def test_player_seat_can_become_active(app):
    """
    Test that PlayerSeat can change to the active state.
    """

    bidding_page = BiddingPage()

    player = bidding_page.players[
        Position.SOUTH
    ]

    seat = PlayerSeat(
        player,
        active=False,
    )

    seat.set_active(True)

    assert seat.active is True

    seat.set_active(False)

    assert seat.active is False

    seat.close()
    bidding_page.close()


def test_player_seat_displays_thirteen_cards(app):
    """
    A newly dealt bridge hand should contain 13 cards.
    """

    bidding_page = BiddingPage()

    player = bidding_page.players[
        Position.SOUTH
    ]

    seat = PlayerSeat(player)

    assert len(player.hand) == 13

    assert len(seat.cards) == 13

    seat.close()
    bidding_page.close()


# =========================================================
# NEW GAME
# =========================================================

def test_new_game_resets_play_page(main_window):
    """
    Starting a new game should reset the existing PlayPage.
    """

    main_window.play_data = {
        "test": "data"
    }

    main_window.play_page.game_complete = True

    main_window.start_new_game()

    assert main_window.play_data is None

    assert main_window.play_page.game_complete is False

    assert (
        main_window.pages.currentWidget()
        == main_window.bidding_page
    )


# =========================================================
# RESUME GAME
# =========================================================

def test_has_unfinished_game_returns_false_when_history_empty(
    main_window,
):
    """
    A new application with no history should not report
    an unfinished game.
    """

    assert main_window.history_manager.games == []

    assert main_window.has_unfinished_game() is False


def test_has_unfinished_game_returns_true_for_incomplete_game(
    main_window,
):
    """
    An incomplete latest game should be detected as resumable.

    GameRecord.is_complete is a read-only property. A game is
    incomplete when it contains fewer than 13 completed tricks.
    """

    game = main_window.history_manager.add_game(
        dealer=Position.SOUTH,
        players=[],
    )

    assert game.is_complete is False

    assert main_window.has_unfinished_game() is True


def test_has_unfinished_game_returns_false_for_completed_game(
    main_window,
):
    """
    A completed latest game should not be reported as
    resumable.
    """

    game = main_window.history_manager.add_game(
        dealer=Position.SOUTH,
        players=[],
    )

    for number in range(1, 14):

        game.add_trick(
            trick_number=number,
            plays={},
        )

    assert game.is_complete is True

    assert main_window.has_unfinished_game() is False


# =========================================================
# REPLAY / PLAY THIS DEAL
# =========================================================

def create_test_game(main_window, dealer, board_number):
    """
    Create a valid historical game containing a complete
    52-card deal.

    This prevents HistoryPage from encountering an invalid
    empty player set while displaying the test game.
    """

    players = new_deal(
        dealer=dealer,
        seed=42,
    )

    game = main_window.history_manager.add_game(
        dealer=dealer,
        players=players,
        board_number=board_number,
    )

    return game


def test_play_existing_deal_navigates_to_bidding(
    main_window,
):
    """
    Selecting Play This Deal should start the selected deal
    from the Bidding page.
    """

    game = create_test_game(
        main_window,
        dealer=Position.SOUTH,
        board_number=5,
    )

    main_window.play_existing_deal(game)

    assert (
        main_window.pages.currentWidget()
        == main_window.bidding_page
    )

    assert main_window.page_title.text() == "Bidding"


def test_play_existing_deal_preserves_dealer(
    main_window,
):
    """
    Replay should use the historical game's dealer.
    """

    game = create_test_game(
        main_window,
        dealer=Position.WEST,
        board_number=7,
    )

    main_window.play_existing_deal(game)

    assert (
        main_window.bidding_page.dealer
        == Position.WEST
    )


def test_play_existing_deal_preserves_board_number(
    main_window,
):
    """
    Replay should use the historical board number.
    """

    game = create_test_game(
        main_window,
        dealer=Position.NORTH,
        board_number=12,
    )

    main_window.play_existing_deal(game)

    assert (
        main_window.bidding_page.board_number
        == 12
    )


def test_play_existing_deal_does_not_set_play_data(
    main_window,
):
    """
    Replay starts a fresh bidding/play session rather than
    resuming the old game state.
    """

    game = create_test_game(
        main_window,
        dealer=Position.EAST,
        board_number=3,
    )

    main_window.play_data = {
        "old": "data"
    }

    main_window.play_existing_deal(game)

    assert main_window.play_data is None


# =========================================================
# HISTORY
# =========================================================

def test_history_page_uses_play_deal_callback(
    main_window,
):
    """
    The HistoryPage should have a callback available for
    starting a replay of an existing deal.
    """

    assert main_window.history_page is not None

    assert (
        main_window.history_page.play_deal_callback
        is not None
    )


# =========================================================
# MAIN WINDOW GAME STATE
# =========================================================

def test_main_window_starts_with_valid_dealer(
    main_window,
):
    """
    MainWindow should have a valid initial dealer.
    """

    assert main_window.current_dealer == Position.SOUTH


def test_main_window_starts_with_board_one(
    main_window,
):
    """
    The first board should be board 1.
    """

    assert main_window.board_number == 1