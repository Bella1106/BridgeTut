"""
Tests for game_logic.tutorial_bbo_examples.
"""

from __future__ import annotations

from game_logic.bbo_parser import BBOGameData
from game_logic.tutorial_bbo_examples import (
    BBO_TUTORIALS,
    get_bbo_tutorial_path,
    get_bbo_tutorials,
    load_bbo_tutorial,
)
from bidding.bid import Denomination
from game_logic.vulnerability import Vulnerability
from card_model.player import Position


def test_bbo_tutorials_are_available() -> None:
    tutorials = get_bbo_tutorials()

    assert len(tutorials) == 2


def test_bbo_tutorial_names() -> None:
    tutorials = get_bbo_tutorials()

    assert tutorials[0].name == "Game 20"
    assert tutorials[1].name == "Hand 16"


def test_bbo_tutorial_filenames() -> None:
    tutorials = get_bbo_tutorials()

    assert tutorials[0].filename == "25-07-2026-game20.txt"
    assert tutorials[1].filename == "260725-hand16.txt"


def test_bbo_tutorial_files_exist() -> None:
    for tutorial in BBO_TUTORIALS:
        path = get_bbo_tutorial_path(tutorial)

        assert path.is_file(), (
            f"BBO tutorial file not found: {path}"
        )


def test_load_game_20_tutorial() -> None:
    tutorial = BBO_TUTORIALS[0]

    game = load_bbo_tutorial(tutorial)

    assert isinstance(game, BBOGameData)
    assert game.dealer == Position.WEST
    assert game.vulnerability == Vulnerability.BOTH

    assert all(
        len(hand) == 13
        for hand in game.hands.values()
    )


def test_load_hand_16_tutorial() -> None:
    tutorial = BBO_TUTORIALS[1]

    game = load_bbo_tutorial(tutorial)

    assert isinstance(game, BBOGameData)
    assert game.dealer == Position.WEST
    assert game.vulnerability == Vulnerability.EAST_WEST

    assert all(
        len(hand) == 13
        for hand in game.hands.values()
    )


def test_load_game_20_makeable_tricks() -> None:
    game = load_bbo_tutorial(BBO_TUTORIALS[0])

    assert game.makeable_tricks[Position.NORTH] == {
        Denomination.CLUBS: 5,
        Denomination.DIAMONDS: 5,
        Denomination.HEARTS: 6,
        Denomination.SPADES: 6,
        Denomination.NO_TRUMP: 6,
    }

    assert game.makeable_tricks[Position.SOUTH] == {
        Denomination.CLUBS: 5,
        Denomination.DIAMONDS: 5,
        Denomination.HEARTS: 6,
        Denomination.SPADES: 6,
        Denomination.NO_TRUMP: 6,
    }


def test_load_hand_16_makeable_tricks() -> None:
    game = load_bbo_tutorial(BBO_TUTORIALS[1])

    assert game.makeable_tricks[Position.EAST] == {
        Denomination.CLUBS: 3,
        Denomination.DIAMONDS: 2,
        Denomination.HEARTS: 2,
        Denomination.SPADES: 3,
        Denomination.NO_TRUMP: 2,
    }

    assert game.makeable_tricks[Position.WEST] == {
        Denomination.CLUBS: 3,
        Denomination.DIAMONDS: 2,
        Denomination.HEARTS: 2,
        Denomination.SPADES: 3,
        Denomination.NO_TRUMP: 2,
    }