import pytest

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow

from card_model.player import Position


# =========================================================
# QT FIXTURE
# =========================================================

@pytest.fixture
def app():
    """
    Create a QApplication for the integration tests.
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
    Create a fresh BridgeTut MainWindow.
    """

    window = MainWindow()

    yield window

    window.close()


# =========================================================
# MAIN WINDOW -> BIDDING
# =========================================================

def test_main_window_contains_bidding_page(main_window):
    """
    Test that MainWindow creates and stores the BiddingPage.
    """

    assert main_window.bidding_page is not None

    assert (
        main_window.bidding_page
        in [
            main_window.pages.widget(i)
            for i in range(main_window.pages.count())
        ]
    )


def test_bidding_page_is_connected_to_navigation(main_window):
    """
    Test that navigating through the main window actually
    displays the BiddingPage.
    """

    main_window.navigate("Bidding")

    assert (
        main_window.pages.currentWidget()
        == main_window.bidding_page
    )


# =========================================================
# BIDDING SYSTEM INTEGRATION
# =========================================================

def test_bidding_page_uses_existing_bidding_system(
    main_window
):
    """
    Test that the GUI has an existing BiddingSystem
    instance available.

    The GUI does not replace the backend bidding system.
    """

    bidding_page = main_window.bidding_page

    assert bidding_page.bidding_system is not None


def test_bidding_page_has_complete_deal(
    main_window
):
    """
    Test that the bidding GUI receives the four players
    from the existing card/deal model.
    """

    bidding_page = main_window.bidding_page

    assert bidding_page.players is not None

    assert len(bidding_page.players) == 4

    for position in [
        Position.NORTH,
        Position.SOUTH,
        Position.EAST,
        Position.WEST,
    ]:

        assert position in bidding_page.players

        assert bidding_page.players[position] is not None


def test_each_player_has_thirteen_cards(
    main_window
):
    """
    Test that the GUI is displaying a valid four-player
    bridge deal from the existing card model.
    """

    bidding_page = main_window.bidding_page

    for position in [
        Position.NORTH,
        Position.SOUTH,
        Position.EAST,
        Position.WEST,
    ]:

        player = bidding_page.players[position]

        assert len(player.hand) == 13


# =========================================================
# BIDDING -> PLAY DATA
# =========================================================

def test_play_page_can_receive_bidding_data(
    main_window
):
    """
    Test the connection between BiddingPage and PlayPage.

    The same players/deal created by BiddingPage are passed
    to PlayPage through MainWindow.play_data.
    """

    bidding_page = main_window.bidding_page

    main_window.play_data = {
        "players": bidding_page.players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    main_window.navigate("Play")

    play_page = main_window.play_page

    assert play_page.players is bidding_page.players

    assert play_page.dealer == bidding_page.dealer


def test_play_page_uses_same_deal_as_bidding_page(
    main_window
):
    """
    PlayPage must use the deal created by BiddingPage
    rather than creating a second independent deal.
    """

    bidding_page = main_window.bidding_page

    original_players = bidding_page.players

    main_window.play_data = {
        "players": original_players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    main_window.navigate("Play")

    assert (
        main_window.play_page.players
        is original_players
    )


# =========================================================
# PLAY PAGE INITIALISATION
# =========================================================

def test_play_page_loads_when_navigated_to(
    main_window
):
    """
    Navigating to Play should load the game data.
    """

    bidding_page = main_window.bidding_page

    main_window.play_data = {
        "players": bidding_page.players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    main_window.navigate("Play")

    play_page = main_window.play_page

    assert play_page.players is not None

    assert play_page.dealer == bidding_page.dealer

    assert play_page.game_loaded is True


# =========================================================
# PLAY PAGE -> PLAYER SEATS
# =========================================================

def test_play_page_creates_four_player_seats(
    main_window
):
    """
    PlayPage should create a seat for each bridge position.
    """

    bidding_page = main_window.bidding_page

    main_window.play_data = {
        "players": bidding_page.players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    main_window.navigate("Play")

    play_page = main_window.play_page

    assert len(play_page.player_seats) == 4

    assert Position.NORTH in play_page.player_seats
    assert Position.SOUTH in play_page.player_seats
    assert Position.EAST in play_page.player_seats
    assert Position.WEST in play_page.player_seats


# =========================================================
# PLAY CARD INTEGRATION
# =========================================================

def test_play_page_can_process_card_click(
    main_window
):
    """
    Test that PlayPage accepts a card from the current
    player's hand and moves it into the played-card area.

    This tests the GUI behaviour, not Alonso's play
    validation rules.
    """

    bidding_page = main_window.bidding_page

    main_window.play_data = {
        "players": bidding_page.players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    main_window.navigate("Play")

    play_page = main_window.play_page

    current_player = play_page.current_player

    assert current_player is not None

    player = play_page.players[current_player]

    assert len(player.hand) == 13

    # Hand is not subscriptable, so obtain the first
    # card using the existing Hand API.
    card = player.hand.sorted_by_suit()[0]

    play_page.play_card(card)

    assert card in play_page.played_cards.values()

    assert len(player.hand) == 12


def test_played_card_is_removed_from_player_hand(
    main_window
):
    """
    Once a card is played, it should no longer remain
    in the player's hand.
    """

    bidding_page = main_window.bidding_page

    main_window.play_data = {
        "players": bidding_page.players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    main_window.navigate("Play")

    play_page = main_window.play_page

    current_player = play_page.current_player

    player = play_page.players[current_player]

    card = player.hand.sorted_by_suit()[0]

    play_page.play_card(card)

    assert card not in player.hand


# =========================================================
# PLAY -> HISTORY
# =========================================================

def test_play_page_creates_game_record(
    main_window
):
    """
    Test that loading a game creates a GameRecord through
    the MainWindow's HistoryManager.
    """

    bidding_page = main_window.bidding_page

    main_window.play_data = {
        "players": bidding_page.players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    main_window.navigate("Play")

    play_page = main_window.play_page

    assert play_page.game_record is not None


def test_game_record_belongs_to_history_manager(
    main_window
):
    """
    Test that the PlayPage creates its game record through
    the MainWindow HistoryManager.
    """

    bidding_page = main_window.bidding_page

    main_window.play_data = {
        "players": bidding_page.players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    main_window.navigate("Play")

    play_page = main_window.play_page

    assert play_page.game_record is not None

    assert main_window.history_manager is not None


# =========================================================
# PLAY -> HISTORY NAVIGATION
# =========================================================

def test_can_navigate_from_play_to_history(
    main_window
):
    """
    Test that the application can move from the Play page
    to the History page.
    """

    main_window.navigate("Play")

    main_window.navigate("History")

    assert (
        main_window.pages.currentWidget()
        == main_window.history_page
    )


def test_history_page_uses_history_manager(
    main_window
):
    """
    Test that HistoryPage is connected to the same
    HistoryManager used by the PlayPage.
    """

    assert main_window.history_manager is not None

    assert main_window.history_page is not None


# =========================================================
# NEW GAME INTEGRATION
# =========================================================

def test_new_game_creates_fresh_bidding_page(
    main_window
):
    """
    Starting a new game should replace the old BiddingPage
    with a fresh one.
    """

    old_bidding_page = main_window.bidding_page

    main_window.start_new_game()

    new_bidding_page = main_window.bidding_page

    assert new_bidding_page is not old_bidding_page

    assert new_bidding_page is not None

    assert new_bidding_page.bidding_system is not None


def test_new_game_creates_fresh_deal(
    main_window
):
    """
    A new BiddingPage should have its own deal.
    """

    old_players = main_window.bidding_page.players

    main_window.start_new_game()

    new_players = main_window.bidding_page.players

    assert new_players is not old_players

    assert len(new_players) == 4


def test_new_game_returns_to_bidding(
    main_window
):
    """
    Starting a new game should take the user to the
    Bidding page.
    """

    main_window.start_new_game()

    assert (
        main_window.pages.currentWidget()
        == main_window.bidding_page
    )

    assert main_window.page_title.text() == "Bidding"


# =========================================================
# HISTORY INTEGRATION
# =========================================================

def test_play_game_is_added_to_history_manager(
    main_window
):
    """
    Loading a game through PlayPage should result in a
    GameRecord being created in the HistoryManager.
    """

    bidding_page = main_window.bidding_page

    main_window.play_data = {
        "players": bidding_page.players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    main_window.navigate("Play")

    play_page = main_window.play_page

    assert play_page.game_record is not None

    assert play_page.game_record.game_id is not None


# =========================================================
# COMPLETE GUI FLOW
# =========================================================

def test_basic_game_gui_flow(main_window):
    """
    Test the basic GUI flow:

        Home
          ->
        Bidding
          ->
        Play
          ->
        History
    """

    # -----------------------------------------------------
    # START AT HOME
    # -----------------------------------------------------

    assert (
        main_window.pages.currentWidget()
        == main_window.home_page
    )

    # -----------------------------------------------------
    # GO TO BIDDING
    # -----------------------------------------------------

    main_window.navigate("Bidding")

    assert (
        main_window.pages.currentWidget()
        == main_window.bidding_page
    )

    # -----------------------------------------------------
    # PASS BIDDING DATA TO PLAY
    # -----------------------------------------------------

    bidding_page = main_window.bidding_page

    main_window.play_data = {
        "players": bidding_page.players,
        "dealer": bidding_page.dealer,
        "contract": None,
        "declarer": None,
        "history": [],
    }

    # -----------------------------------------------------
    # GO TO PLAY
    # -----------------------------------------------------

    main_window.navigate("Play")

    assert (
        main_window.pages.currentWidget()
        == main_window.play_page
    )

    assert main_window.play_page.game_loaded is True

    # -----------------------------------------------------
    # GO TO HISTORY
    # -----------------------------------------------------

    main_window.navigate("History")

    assert (
        main_window.pages.currentWidget()
        == main_window.history_page
    )