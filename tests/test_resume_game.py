"""
Tests for resuming an unfinished BridgeTut game.

Resume means:
- The existing GameRecord is reused.
- The game ID stays the same.
- The dealer and board stay the same.
- The players/cards stay the same.
- Saved in-progress play state stays the same.
- No new game is created.
"""

from copy import deepcopy

from card_model.deck import new_deal
from card_model.player import Position
from game_history.history_manager import HistoryManager


def create_test_manager(tmp_path, monkeypatch):
    """Create an isolated HistoryManager for this test."""

    history_file = tmp_path / "history.pkl"

    monkeypatch.setattr(
        HistoryManager,
        "HISTORY_FILE",
        history_file,
    )

    return HistoryManager()


def create_test_players():
    """Create a deterministic legal Bridge deal."""

    return new_deal(
        dealer=Position.SOUTH,
        seed=42,
    )


def get_player(players, position):
    """Return a player by position."""

    if isinstance(players, dict):
        return players[position]

    for player in players:
        if player.position == position:
            return player

    raise AssertionError(
        f"Could not find player at {position}"
    )


def get_first_card(player):
    """Return the first card from a Hand."""

    for card in player.hand:
        return card

    raise AssertionError(
        f"{player.position} has no cards"
    )


def test_resume_preserves_game_id(tmp_path, monkeypatch):
    """Resuming a game keeps the original game ID."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=1,
    )

    original_id = game.game_id

    resumed_game = manager.get_latest_game()

    assert resumed_game is not None
    assert resumed_game.game_id == original_id


def test_resume_preserves_dealer(tmp_path, monkeypatch):
    """Resuming a game keeps the original dealer."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.WEST,
        players=deepcopy(players),
        board_number=2,
    )

    resumed_game = manager.get_latest_game()

    assert resumed_game.dealer == game.dealer
    assert resumed_game.dealer == Position.WEST


def test_resume_preserves_board_number(tmp_path, monkeypatch):
    """Resuming a game keeps the original board number."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=15,
    )

    resumed_game = manager.get_latest_game()

    assert resumed_game.board_number == game.board_number
    assert resumed_game.board_number == 15


def test_resume_preserves_players(tmp_path, monkeypatch):
    """Resuming a game preserves all four players."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=3,
    )

    resumed_game = manager.get_latest_game()

    for position in Position:

        original_player = get_player(
            game.players,
            position,
        )

        resumed_player = get_player(
            resumed_game.players,
            position,
        )

        assert resumed_player.position == original_player.position
        assert resumed_player.hand == original_player.hand


def test_resume_preserves_current_player(tmp_path, monkeypatch):
    """Resuming preserves whose turn it currently is."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=4,
    )

    game.current_player = Position.NORTH

    resumed_game = manager.get_latest_game()

    assert resumed_game.current_player == Position.NORTH


def test_resume_preserves_current_trick_number(tmp_path, monkeypatch):
    """Resuming preserves the current trick number."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=5,
    )

    game.current_trick_number = 4

    resumed_game = manager.get_latest_game()

    assert resumed_game.current_trick_number == 4


def test_resume_preserves_played_cards(tmp_path, monkeypatch):
    """Resuming preserves cards that have already been played."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=6,
    )

    north = get_player(
        game.players,
        Position.NORTH,
    )

    east = get_player(
        game.players,
        Position.EAST,
    )

    north_card = get_first_card(north)
    east_card = get_first_card(east)

    played_cards = {
        Position.NORTH: north_card,
        Position.EAST: east_card,
    }

    game.current_played_cards = played_cards

    resumed_game = manager.get_latest_game()

    assert resumed_game.current_played_cards == played_cards


def test_resume_preserves_contract_and_declarer(
    tmp_path,
    monkeypatch,
):
    """Resuming preserves the existing contract and declarer."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=7,
    )

    game.contract = "3NT"
    game.declarer = Position.NORTH

    resumed_game = manager.get_latest_game()

    assert resumed_game.contract == "3NT"
    assert resumed_game.declarer == Position.NORTH


def test_resume_preserves_bidding_history(
    tmp_path,
    monkeypatch,
):
    """Resuming preserves the existing bidding history."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    bidding_history = [
        "1NT",
        "Pass",
        "3NT",
        "Pass",
        "Pass",
        "Pass",
    ]

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        bidding_history=bidding_history,
        board_number=8,
    )

    resumed_game = manager.get_latest_game()

    assert resumed_game.bidding_history == bidding_history


def test_resume_does_not_create_new_game(
    tmp_path,
    monkeypatch,
):
    """Resuming must not add another GameRecord."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=9,
    )

    original_id = game.game_id

    games_before = manager.get_games()

    resumed_game = manager.get_latest_game()

    games_after = manager.get_games()

    assert resumed_game.game_id == original_id
    assert len(games_after) == len(games_before)

    matching_games = [
        saved_game
        for saved_game in games_after
        if saved_game.game_id == original_id
    ]

    assert len(matching_games) == 1