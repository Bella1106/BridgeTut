import pytest

from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from gui.history_page import HistoryPage

from game_history.history_manager import HistoryManager
from card_model.player import Position
from card_model.deck import new_deal


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
# ISOLATED HISTORY FIXTURE
# =========================================================

@pytest.fixture
def isolated_history(tmp_path, monkeypatch):
    """
    Give each test a temporary history file.

    This prevents the integration tests from loading the
    real game_history/history.pkl containing existing games.
    """

    history_file = tmp_path / "history.pkl"

    monkeypatch.setattr(
        HistoryManager,
        "HISTORY_FILE",
        history_file,
    )

    return HistoryManager()


# =========================================================
# MAIN WINDOW FIXTURE
# =========================================================

@pytest.fixture
def main_window(app, tmp_path, monkeypatch):
    """
    Create a fresh BridgeTut MainWindow using an isolated
    temporary HistoryManager file.
    """

    history_file = tmp_path / "history.pkl"

    monkeypatch.setattr(
        HistoryManager,
        "HISTORY_FILE",
        history_file,
    )

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

def test_bidding_page_uses_existing_bidding_system(main_window):
    """
    Test that the GUI has an existing BiddingSystem
    instance available.

    The GUI does not replace the backend bidding system.
    """

    bidding_page = main_window.bidding_page

    assert bidding_page.bidding_system is not None


def test_bidding_page_has_complete_deal(main_window):
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


def test_each_player_has_thirteen_cards(main_window):
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

def test_play_page_can_receive_bidding_data(main_window):
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


def test_play_page_uses_same_deal_as_bidding_page(main_window):
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

def test_play_page_loads_when_navigated_to(main_window):
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

def test_play_page_creates_four_player_seats(main_window):
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

def test_play_page_can_process_card_click(main_window):
    """
    Test that PlayPage accepts a card from the current
    player's hand and moves it into the played-card area.

    This test focuses on GUI card-play behaviour rather
    than bidding or contract logic.
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

    # There is no contract/declarer in this test, so the
    # normal play-turn setup does not establish a player.
    # Set one explicitly because this test is only testing
    # card interaction.
    play_page.current_player = bidding_page.dealer

    current_player = play_page.current_player

    assert current_player is not None

    player = play_page.players[current_player]

    assert len(player.hand) == 13

    # Hand is not subscriptable, so use the existing Hand API.
    card = player.hand.sorted_by_suit()[0]

    play_page.play_card(card)

    assert card in play_page.played_cards.values()
    assert len(player.hand) == 12


def test_played_card_is_removed_from_player_hand(main_window):
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

    # Establish a player explicitly because this test does
    # not need to exercise contract/declarer setup.
    play_page.current_player = bidding_page.dealer

    current_player = play_page.current_player

    assert current_player is not None

    player = play_page.players[current_player]

    assert len(player.hand) == 13

    card = player.hand.sorted_by_suit()[0]

    play_page.play_card(card)

    assert card not in player.hand
    assert len(player.hand) == 12


# =========================================================
# PLAY -> HISTORY
# =========================================================

def test_play_page_creates_game_record(main_window):
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


def test_game_record_belongs_to_history_manager(main_window):
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

    assert (
        main_window.history_manager.get_game(
            play_page.game_record.game_id
        )
        is play_page.game_record
    )


# =========================================================
# PLAY -> HISTORY NAVIGATION
# =========================================================

def test_can_navigate_from_play_to_history(main_window):
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


def test_history_page_uses_history_manager(main_window):
    """
    Test that HistoryPage is connected to the same
    HistoryManager used by MainWindow.
    """

    assert main_window.history_manager is not None
    assert main_window.history_page is not None

    assert (
        main_window.history_page.history_manager
        is main_window.history_manager
    )


# =========================================================
# NEW GAME INTEGRATION
# =========================================================

def test_new_game_creates_fresh_bidding_page(main_window):
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


def test_new_game_creates_fresh_deal(main_window):
    """
    A new BiddingPage should have its own deal.
    """

    old_players = main_window.bidding_page.players

    main_window.start_new_game()

    new_players = main_window.bidding_page.players

    assert new_players is not old_players
    assert len(new_players) == 4

    for position in Position:
        assert len(new_players[position].hand) == 13


def test_new_game_returns_to_bidding(main_window):
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

def test_play_game_is_added_to_history_manager(main_window):
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

    games = main_window.history_manager.get_games()

    assert any(
        game.game_id == play_page.game_record.game_id
        for game in games
    )


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


# =========================================================
# UNFINISHED GAME / RESUME INTEGRATION
# =========================================================

def test_has_unfinished_game_returns_false_when_history_empty(
    main_window,
):
    """
    No history means there is no unfinished game.
    """

    assert main_window.has_unfinished_game() is False


def test_has_unfinished_game_returns_true_for_incomplete_game(
    main_window,
):
    """
    A GameRecord with fewer than 13 completed tricks is
    considered unfinished.
    """

    players = new_deal(
        Position.SOUTH,
        seed=42,
    )

    game = main_window.history_manager.add_game(
        dealer=Position.SOUTH,
        players=players,
        board_number=1,
    )

    assert game.is_complete is False
    assert main_window.has_unfinished_game() is True


def test_has_unfinished_game_returns_false_for_completed_game(
    main_window,
):
    """
    A GameRecord with 13 completed tricks is considered
    complete.
    """

    players = new_deal(
        Position.SOUTH,
        seed=42,
    )

    game = main_window.history_manager.add_game(
        dealer=Position.SOUTH,
        players=players,
        board_number=1,
    )

    for trick_number in range(1, 14):
        game.add_trick(
            trick_number,
            {},
        )

    assert game.is_complete is True
    assert main_window.has_unfinished_game() is False


# =========================================================
# REPLAY EXISTING DEAL
# =========================================================

def create_history_game(
    main_window,
    dealer=Position.SOUTH,
    board=7,
):
    """
    Helper for replay tests.

    Creates a valid historical game with a deterministic
    four-player deal.
    """

    players = new_deal(
        dealer,
        seed=42,
    )

    return main_window.history_manager.add_game(
        dealer=dealer,
        players=players,
        board_number=board,
    )


def test_play_existing_deal_navigates_to_bidding(main_window):
    """
    Playing an existing historical deal should return the
    user to a fresh BiddingPage.
    """

    game = create_history_game(
        main_window,
        dealer=Position.SOUTH,
        board=7,
    )

    main_window.play_existing_deal(game)

    assert (
        main_window.pages.currentWidget()
        == main_window.bidding_page
    )


def test_play_existing_deal_preserves_dealer(main_window):
    """
    Replay should use the historical game's dealer.
    """

    game = create_history_game(
        main_window,
        dealer=Position.WEST,
        board=7,
    )

    main_window.play_existing_deal(game)

    assert (
        main_window.bidding_page.dealer
        == Position.WEST
    )


def test_play_existing_deal_preserves_board_number(main_window):
    """
    Replay should use the historical game's board number.
    """

    game = create_history_game(
        main_window,
        dealer=Position.NORTH,
        board=25,
    )

    main_window.play_existing_deal(game)

    assert (
        main_window.bidding_page.board_number
        == 25
    )


def test_play_existing_deal_does_not_set_play_data(
    main_window,
):
    """
    Replay starts from bidding, so it should not populate
    MainWindow.play_data with the old game's bidding/play
    state.
    """

    game = create_history_game(
        main_window,
        dealer=Position.SOUTH,
        board=10,
    )

    main_window.play_data = {
        "old": "data",
    }

    main_window.play_existing_deal(game)

    assert main_window.play_data is None


def test_play_existing_deal_uses_same_cards(main_window):
    """
    Replay should contain the same 52 cards as the historical
    deal.
    """

    game = create_history_game(
        main_window,
        dealer=Position.SOUTH,
        board=7,
    )

    original_cards = {}

    for position, player in game.players.items():
        original_cards[position] = set(player.hand)

    main_window.play_existing_deal(game)

    replay_players = main_window.bidding_page.players

    for position in Position:
        replay_cards = set(
            replay_players[position].hand
        )

        assert replay_cards == original_cards[position]


def test_play_existing_deal_keeps_historical_game(
    main_window,
):
    """
    Replaying a historical game must not delete the original
    historical record.
    """

    game = create_history_game(
        main_window,
        dealer=Position.SOUTH,
        board=7,
    )

    original_game_id = game.game_id

    main_window.play_existing_deal(game)

    stored_game = (
        main_window.history_manager.get_game(
            original_game_id
        )
    )

    assert stored_game is game


# =========================================================
# HISTORY PAGE
# =========================================================

def test_history_page_can_be_created(
    app,
    isolated_history,
):
    """
    HistoryPage should be constructible using an isolated
    HistoryManager.
    """

    page = HistoryPage(
        isolated_history
    )

    assert page is not None

    page.close()


def test_history_page_uses_play_deal_callback(
    app,
    isolated_history,
):
    """
    HistoryPage should retain the callback used to replay
    a historical deal.
    """

    called_games = []

    def callback(game):
        called_games.append(game)

    page = HistoryPage(
        isolated_history,
        play_deal_callback=callback,
    )

    assert page.play_deal_callback is callback

    page.close()


# =========================================================
# MAIN WINDOW INITIAL STATE
# =========================================================

def test_main_window_starts_with_valid_dealer(main_window):
    """
    MainWindow should start with a valid bridge dealer.
    """

    assert main_window.current_dealer in list(Position)


def test_main_window_starts_with_board_one(main_window):
    """
    MainWindow should start at board 1.
    """

    assert main_window.board_number == 1