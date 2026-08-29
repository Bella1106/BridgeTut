import pytest

from PySide6.QtWidgets import QApplication, QLabel

from gui.main_window import MainWindow
from gui.bidding_page import BiddingPage
from gui.play_page import PlayPage
from gui.widgets.card_widget import CardWidget
from gui.widgets.player_seat import PlayerSeat

from card_model.player import Position


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
    """
    window = MainWindow()

    yield window

    window.close()


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
    Test that the main window contains the stacked page
    navigation used by the application.
    """

    assert main_window.pages is not None

    assert main_window.pages.count() >= 6


def test_navigation_buttons_exist(main_window):
    """
    Test that all main navigation buttons are present.
    """

    expected_buttons = [
        "Home",
        "Bidding",
        "Play",
        "Results",
        "History",
    ]

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


def test_can_navigate_to_results(main_window):
    """
    Test that the Results page can be selected.
    """

    main_window.navigate("Results")

    assert (
        main_window.pages.currentWidget()
        == main_window.results_page
    )

    assert main_window.page_title.text() == "Results"


def test_invalid_navigation_does_nothing(main_window):
    """
    Invalid page names should not change the current page.
    """

    main_window.navigate("Home")

    current_page = main_window.pages.currentWidget()

    main_window.navigate("NotARealPage")

    assert main_window.pages.currentWidget() == current_page

    assert main_window.page_title.text() == "Home"


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
    The GUI should contain an existing BiddingSystem
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
    this test does not depend on guessing Alonso's Card
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

    # PlayerSeat uses QLabel widgets for the position,
    # role and card count.
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

    assert main_window.pages.currentWidget() == (
        main_window.bidding_page
    )