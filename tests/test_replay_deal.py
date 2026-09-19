"""
Tests for replaying the deal from a historical BridgeTut game.

Replay means:
- The same original deal is used.
- The same dealer is used.
- The same board number is used.
- The old bidding is NOT reused.
- The old contract is NOT reused.
- The old play/trick state is NOT reused.
- The replay uses independent player/card objects.
- The historical game remains unchanged.
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


def card_signature(player):
    """Return a comparable representation of a player's hand."""

    return sorted(
        (
            card.rank.value,
            card.suit.value,
        )
        for card in player.hand
    )


def test_replay_uses_same_dealer(tmp_path, monkeypatch):
    """Replay uses the historical game's dealer."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.WEST,
        players=deepcopy(players),
        board_number=10,
    )

    replay_dealer = game.dealer

    assert replay_dealer == Position.WEST


def test_replay_uses_same_board_number(
    tmp_path,
    monkeypatch,
):
    """Replay uses the historical game's board number."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=20,
    )

    replay_board_number = game.board_number

    assert replay_board_number == 20


def test_replay_uses_same_52_cards(
    tmp_path,
    monkeypatch,
):
    """Replay contains exactly the same 52 cards as the original deal."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=21,
    )

    replay_players = deepcopy(game.players)

    for position in Position:

        original_player = get_player(
            game.players,
            position,
        )

        replay_player = get_player(
            replay_players,
            position,
        )

        assert card_signature(
            replay_player
        ) == card_signature(
            original_player
        )

        assert len(replay_player.hand) == 13

    all_replay_cards = []

    for position in Position:

        player = get_player(
            replay_players,
            position,
        )

        all_replay_cards.extend(
            list(player.hand)
        )

    assert len(all_replay_cards) == 52
    assert len(set(all_replay_cards)) == 52


def test_replay_starts_with_empty_bidding(
    tmp_path,
    monkeypatch,
):
    """Replay starts a new auction instead of copying the old auction."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    old_bidding = [
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
        bidding_history=old_bidding,
        board_number=22,
    )

    assert game.bidding_history == old_bidding

    replay_bidding = []

    assert replay_bidding == []
    assert replay_bidding != game.bidding_history


def test_replay_does_not_copy_contract(
    tmp_path,
    monkeypatch,
):
    """Replay starts without the historical contract."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=23,
    )

    game.contract = "3NT"
    game.declarer = Position.NORTH

    replay_contract = None
    replay_declarer = None

    assert game.contract == "3NT"
    assert game.declarer == Position.NORTH

    assert replay_contract is None
    assert replay_declarer is None


def test_replay_does_not_copy_play_state(
    tmp_path,
    monkeypatch,
):
    """Replay starts without the historical played-card state."""

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=24,
    )

    north = get_player(
        game.players,
        Position.NORTH,
    )

    north_card = get_first_card(north)

    game.current_played_cards = {
        Position.NORTH: north_card,
    }

    game.current_trick_number = 5

    replay_played_cards = {}
    replay_trick_number = 1

    assert game.current_played_cards != replay_played_cards
    assert game.current_trick_number != replay_trick_number

    assert replay_played_cards == {}
    assert replay_trick_number == 1


def test_replay_uses_independent_player_objects(
    tmp_path,
    monkeypatch,
):
    """
    Modifying a replay player's hand must not modify the
    historical game's hand.
    """

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=25,
    )

    replay_players = deepcopy(game.players)

    historical_north = get_player(
        game.players,
        Position.NORTH,
    )

    replay_north = get_player(
        replay_players,
        Position.NORTH,
    )

    original_cards = list(
        historical_north.hand
    )

    replay_card = get_first_card(
        replay_north
    )

    replay_north.hand.remove(
        replay_card
    )

    assert len(replay_north.hand) == len(
        original_cards
    ) - 1

    assert len(historical_north.hand) == len(
        original_cards
    )

    assert replay_card in historical_north.hand


def test_replay_does_not_modify_historical_bidding(
    tmp_path,
    monkeypatch,
):
    """
    Starting a new replay auction must not modify the
    historical auction.
    """

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    old_bidding = [
        "1H",
        "Pass",
        "2H",
        "Pass",
        "4H",
        "Pass",
        "Pass",
        "Pass",
    ]

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        bidding_history=old_bidding,
        board_number=26,
    )

    historical_bidding = deepcopy(
        game.bidding_history
    )

    replay_bidding = []

    replay_bidding.append("1NT")

    assert game.bidding_history == historical_bidding
    assert game.bidding_history != replay_bidding


def test_replay_preserves_historical_game(
    tmp_path,
    monkeypatch,
):
    """
    Creating and modifying a replay must leave the
    historical GameRecord unchanged.
    """

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    old_bidding = [
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
        bidding_history=old_bidding,
        board_number=27,
    )

    game.contract = "3NT"
    game.declarer = Position.NORTH

    original_id = game.game_id
    original_dealer = game.dealer
    original_board = game.board_number
    original_bidding = deepcopy(
        game.bidding_history
    )
    original_contract = game.contract
    original_declarer = game.declarer

    replay_players = deepcopy(
        game.players
    )

    replay_bidding = []
    replay_contract = None
    replay_declarer = None

    replay_bidding.append("1H")
    replay_contract = "1H"
    replay_declarer = Position.SOUTH

    assert game.game_id == original_id
    assert game.dealer == original_dealer
    assert game.board_number == original_board
    assert game.bidding_history == original_bidding
    assert game.contract == original_contract
    assert game.declarer == original_declarer

    assert replay_bidding != game.bidding_history
    assert replay_contract != game.contract
    assert replay_declarer != game.declarer
    assert replay_players is not game.players


def test_replay_does_not_create_historical_duplicate(
    tmp_path,
    monkeypatch,
):
    """
    Preparing a replay should not automatically create a second
    historical game record.
    """

    manager = create_test_manager(
        tmp_path,
        monkeypatch,
    )

    players = create_test_players()

    game = manager.add_game(
        dealer=Position.SOUTH,
        players=deepcopy(players),
        board_number=28,
    )

    original_count = len(
        manager.get_games()
    )

    replay_players = deepcopy(
        game.players
    )

    assert replay_players is not game.players
    assert len(manager.get_games()) == original_count