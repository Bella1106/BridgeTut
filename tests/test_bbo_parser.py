"""
test_bbo_parser.py
------------------
Tests for game_logic.bbo_parser.

The tests use the same HTML structure as the BBO examples supplied
for the BridgeTut project.

These tests verify that the parser correctly extracts:
    - all four hands
    - the dealer
    - vulnerability
    - the makeable-tricks table

They also verify that invalid BBO deals are rejected.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bidding.bid import Denomination
from card_model.card import Card, Rank, Suit
from card_model.player import Position
from game_logic.bbo_parser import parse_bbo_file, parse_bbo_html
from game_logic.vulnerability import Vulnerability


# ---------------------------------------------------------------------------
# BBO example 1
# ---------------------------------------------------------------------------

BBO_GAME_20_HTML = """
<!doctype html>
<html lang="en">
<head>
<body>

<div class="component_hand_record">

    <div class="north vulnerable-BOTH">
        <h3>
            North
            <abbr title="Vulnerable" class="has_tooltip">V</abbr>
        </h3>
        <ul>
            <li>
                <i class="spade">&spades;</i>
                <ul>
                    <li>K</li><li>2</li>
                </ul>
            </li>
            <li class="red">
                <i class="heart">&hearts;</i>
                <ul>
                    <li>A</li><li>Q</li><li>7</li><li>3</li>
                </ul>
            </li>
            <li class="red">
                <i class="diamond">&diams;</i>
                <ul>
                    <li>A</li><li>K</li><li>9</li>
                </ul>
            </li>
            <li>
                <i class="club">&clubs;</i>
                <ul>
                    <li>A</li><li>8</li><li>6</li><li>5</li>
                </ul>
            </li>
        </ul>
    </div>

    <div class="west vulnerable-BOTH">
        <h3>
            West
            <abbr title="Vulnerable" class="has_tooltip">V</abbr>
            <abbr title="Dealer" class="has_tooltip">D</abbr>
        </h3>
        <ul>
            <li>
                <i class="spade">&spades;</i>
                <ul>
                    <li>J</li><li>9</li><li>4</li>
                </ul>
            </li>
            <li class="red">
                <i class="heart">&hearts;</i>
                <ul>
                    <li>J</li><li>6</li><li>5</li><li>4</li>
                </ul>
            </li>
            <li class="red">
                <i class="diamond">&diams;</i>
                <ul>
                    <li>J</li><li>6</li><li>5</li>
                </ul>
            </li>
            <li>
                <i class="club">&clubs;</i>
                <ul>
                    <li>K</li><li>10</li><li>9</li>
                </ul>
            </li>
        </ul>
    </div>

    <div class="east vulnerable-BOTH">
        <h3>
            East
            <abbr title="Vulnerable" class="has_tooltip">V</abbr>
        </h3>
        <ul>
            <li>
                <i class="spade">&spades;</i>
                <ul>
                    <li>10</li><li>6</li><li>3</li>
                </ul>
            </li>
            <li class="red">
                <i class="heart">&hearts;</i>
                <ul>
                    <li>9</li><li>8</li><li>2</li>
                </ul>
            </li>
            <li class="red">
                <i class="diamond">&diams;</i>
                <ul>
                    <li>Q</li><li>10</li><li>8</li><li>2</li>
                </ul>
            </li>
            <li>
                <i class="club">&clubs;</i>
                <ul>
                    <li>J</li><li>7</li><li>3</li>
                </ul>
            </li>
        </ul>
    </div>

    <div class="south vulnerable-BOTH">
        <h3>
            South
            <abbr title="Vulnerable" class="has_tooltip">V</abbr>
        </h3>
        <ul>
            <li>
                <i class="spade">&spades;</i>
                <ul>
                    <li>A</li><li>Q</li><li>8</li><li>7</li><li>5</li>
                </ul>
            </li>
            <li class="red">
                <i class="heart">&hearts;</i>
                <ul>
                    <li>K</li><li>10</li>
                </ul>
            </li>
            <li class="red">
                <i class="diamond">&diams;</i>
                <ul>
                    <li>7</li><li>4</li><li>3</li>
                </ul>
            </li>
            <li>
                <i class="club">&clubs;</i>
                <ul>
                    <li>Q</li><li>4</li><li>2</li>
                </ul>
            </li>
        </ul>
    </div>

</div>

<div class="block">
    <div class="component_table">
        <table>
            <thead>
            <tr>
                <th></th>
                <th><i class="club">&clubs;</i></th>
                <th><i class="diamond">&diams;</i></th>
                <th><i class="heart">&hearts;</i></th>
                <th><i class="spade">&spades;</i></th>
                <th>NT</th>
            </tr>
            </thead>

            <tr>
                <td>North</td>
                <td class="text_center">5</td>
                <td class="text_center">5</td>
                <td class="text_center">6</td>
                <td class="text_center">6</td>
                <td class="text_center">6</td>
            </tr>

            <tr>
                <td>South</td>
                <td class="text_center">5</td>
                <td class="text_center">5</td>
                <td class="text_center">6</td>
                <td class="text_center">6</td>
                <td class="text_center">6</td>
            </tr>

            <tr>
                <td>East</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
            </tr>

            <tr>
                <td>West</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
            </tr>
        </table>
    </div>
</div>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# BBO example 2
# ---------------------------------------------------------------------------

BBO_HAND_16_HTML = """
<!doctype html>
<html lang="en">
<body>

<div class="component_hand_record">

    <div class="north vulnerable-EW">
        <h3>
            North
            <abbr title="Not vulnerable" class="has_tooltip">NV</abbr>
        </h3>
        <ul>
            <li>
                <i class="spade">&spades;</i>
                <ul>
                    <li>10</li><li>8</li><li>2</li>
                </ul>
            </li>
            <li class="red">
                <i class="heart">&hearts;</i>
                <ul>
                    <li>Q</li><li>J</li><li>2</li>
                </ul>
            </li>
            <li class="red">
                <i class="diamond">&diams;</i>
                <ul>
                    <li>J</li><li>10</li><li>8</li><li>6</li>
                </ul>
            </li>
            <li>
                <i class="club">&clubs;</i>
                <ul>
                    <li>Q</li><li>3</li><li>2</li>
                </ul>
            </li>
        </ul>
    </div>

    <div class="west vulnerable-EW">
        <h3>
            West
            <abbr title="Vulnerable" class="has_tooltip">V</abbr>
            <abbr title="Dealer" class="has_tooltip">D</abbr>
        </h3>
        <ul>
            <li>
                <i class="spade">&spades;</i>
                <ul>
                    <li>J</li><li>9</li><li>7</li>
                </ul>
            </li>
            <li class="red">
                <i class="heart">&hearts;</i>
                <ul>
                    <li>8</li><li>4</li>
                </ul>
            </li>
            <li class="red">
                <i class="diamond">&diams;</i>
                <ul>
                    <li>K</li><li>Q</li><li>5</li><li>4</li><li>3</li>
                </ul>
            </li>
            <li>
                <i class="club">&clubs;</i>
                <ul>
                    <li>A</li><li>K</li><li>4</li>
                </ul>
            </li>
        </ul>
    </div>

    <div class="east vulnerable-EW">
        <h3>
            East
            <abbr title="Vulnerable" class="has_tooltip">V</abbr>
        </h3>
        <ul>
            <li>
                <i class="spade">&spades;</i>
                <ul>
                    <li>K</li><li>Q</li><li>6</li><li>5</li>
                </ul>
            </li>
            <li class="red">
                <i class="heart">&hearts;</i>
                <ul>
                    <li>A</li><li>10</li><li>9</li><li>7</li>
                </ul>
            </li>
            <li class="red">
                <i class="diamond">&diams;</i>
                <ul>
                    <li>9</li>
                </ul>
            </li>
            <li>
                <i class="club">&clubs;</i>
                <ul>
                    <li>J</li><li>10</li><li>7</li><li>5</li>
                </ul>
            </li>
        </ul>
    </div>

    <div class="south vulnerable-EW">
        <h3>
            South
            <abbr title="Not vulnerable" class="has_tooltip">NV</abbr>
        </h3>
        <ul>
            <li>
                <i class="spade">&spades;</i>
                <ul>
                    <li>A</li><li>4</li><li>3</li>
                </ul>
            </li>
            <li class="red">
                <i class="heart">&hearts;</i>
                <ul>
                    <li>K</li><li>6</li><li>5</li><li>3</li>
                </ul>
            </li>
            <li class="red">
                <i class="diamond">&diams;</i>
                <ul>
                    <li>A</li><li>7</li><li>2</li>
                </ul>
            </li>
            <li>
                <i class="club">&clubs;</i>
                <ul>
                    <li>9</li><li>8</li><li>6</li>
                </ul>
            </li>
        </ul>
    </div>

</div>

<div class="block">
    <div class="component_table">
        <table>
            <thead>
            <tr>
                <th></th>
                <th><i class="club">&clubs;</i></th>
                <th><i class="diamond">&diams;</i></th>
                <th><i class="heart">&hearts;</i></th>
                <th><i class="spade">&spades;</i></th>
                <th>NT</th>
            </tr>
            </thead>

            <tr>
                <td>North</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
            </tr>

            <tr>
                <td>South</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
                <td class="text_center">-</td>
            </tr>

            <tr>
                <td>East</td>
                <td class="text_center">3</td>
                <td class="text_center">2</td>
                <td class="text_center">2</td>
                <td class="text_center">3</td>
                <td class="text_center">2</td>
            </tr>

            <tr>
                <td>West</td>
                <td class="text_center">3</td>
                <td class="text_center">2</td>
                <td class="text_center">2</td>
                <td class="text_center">3</td>
                <td class="text_center">2</td>
            </tr>
        </table>
    </div>
</div>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Card helpers
# ---------------------------------------------------------------------------

def card(rank: Rank, suit: Suit) -> Card:
    """Small helper to make expected cards easier to read."""
    return Card(rank, suit)


# ---------------------------------------------------------------------------
# Example 1 tests
# ---------------------------------------------------------------------------

def test_parse_bbo_game_20_dealer_and_vulnerability() -> None:
    data = parse_bbo_html(BBO_GAME_20_HTML)

    assert data.dealer == Position.WEST
    assert data.vulnerability is Vulnerability.BOTH


def test_parse_bbo_game_20_each_hand_has_13_cards() -> None:
    data = parse_bbo_html(BBO_GAME_20_HTML)

    assert len(data.hands[Position.NORTH]) == 13
    assert len(data.hands[Position.SOUTH]) == 13
    assert len(data.hands[Position.EAST]) == 13
    assert len(data.hands[Position.WEST]) == 13


def test_parse_bbo_game_20_north_hand() -> None:
    data = parse_bbo_html(BBO_GAME_20_HTML)

    expected = [
        card(Rank.KING, Suit.SPADES),
        card(Rank.TWO, Suit.SPADES),

        card(Rank.ACE, Suit.HEARTS),
        card(Rank.QUEEN, Suit.HEARTS),
        card(Rank.SEVEN, Suit.HEARTS),
        card(Rank.THREE, Suit.HEARTS),

        card(Rank.ACE, Suit.DIAMONDS),
        card(Rank.KING, Suit.DIAMONDS),
        card(Rank.NINE, Suit.DIAMONDS),

        card(Rank.ACE, Suit.CLUBS),
        card(Rank.EIGHT, Suit.CLUBS),
        card(Rank.SIX, Suit.CLUBS),
        card(Rank.FIVE, Suit.CLUBS),
    ]

    assert set(data.hands[Position.NORTH]) == set(expected)


def test_parse_bbo_game_20_south_hand() -> None:
    data = parse_bbo_html(BBO_GAME_20_HTML)

    expected = [
        card(Rank.ACE, Suit.SPADES),
        card(Rank.QUEEN, Suit.SPADES),
        card(Rank.EIGHT, Suit.SPADES),
        card(Rank.SEVEN, Suit.SPADES),
        card(Rank.FIVE, Suit.SPADES),

        card(Rank.KING, Suit.HEARTS),
        card(Rank.TEN, Suit.HEARTS),

        card(Rank.SEVEN, Suit.DIAMONDS),
        card(Rank.FOUR, Suit.DIAMONDS),
        card(Rank.THREE, Suit.DIAMONDS),

        card(Rank.QUEEN, Suit.CLUBS),
        card(Rank.FOUR, Suit.CLUBS),
        card(Rank.TWO, Suit.CLUBS),
    ]

    assert set(data.hands[Position.SOUTH]) == set(expected)


def test_parse_bbo_game_20_east_hand() -> None:
    data = parse_bbo_html(BBO_GAME_20_HTML)

    expected = [
        card(Rank.TEN, Suit.SPADES),
        card(Rank.SIX, Suit.SPADES),
        card(Rank.THREE, Suit.SPADES),

        card(Rank.NINE, Suit.HEARTS),
        card(Rank.EIGHT, Suit.HEARTS),
        card(Rank.TWO, Suit.HEARTS),

        card(Rank.QUEEN, Suit.DIAMONDS),
        card(Rank.TEN, Suit.DIAMONDS),
        card(Rank.EIGHT, Suit.DIAMONDS),
        card(Rank.TWO, Suit.DIAMONDS),

        card(Rank.JACK, Suit.CLUBS),
        card(Rank.SEVEN, Suit.CLUBS),
        card(Rank.THREE, Suit.CLUBS),
    ]

    assert set(data.hands[Position.EAST]) == set(expected)


def test_parse_bbo_game_20_west_hand() -> None:
    data = parse_bbo_html(BBO_GAME_20_HTML)

    expected = [
        card(Rank.JACK, Suit.SPADES),
        card(Rank.NINE, Suit.SPADES),
        card(Rank.FOUR, Suit.SPADES),

        card(Rank.JACK, Suit.HEARTS),
        card(Rank.SIX, Suit.HEARTS),
        card(Rank.FIVE, Suit.HEARTS),
        card(Rank.FOUR, Suit.HEARTS),

        card(Rank.JACK, Suit.DIAMONDS),
        card(Rank.SIX, Suit.DIAMONDS),
        card(Rank.FIVE, Suit.DIAMONDS),

        card(Rank.KING, Suit.CLUBS),
        card(Rank.TEN, Suit.CLUBS),
        card(Rank.NINE, Suit.CLUBS),
    ]

    assert set(data.hands[Position.WEST]) == set(expected)


def test_parse_bbo_game_20_makeable_tricks() -> None:
    data = parse_bbo_html(BBO_GAME_20_HTML)

    assert data.makeable_tricks[Position.NORTH][Denomination.CLUBS] == 5
    assert data.makeable_tricks[Position.NORTH][Denomination.DIAMONDS] == 5
    assert data.makeable_tricks[Position.NORTH][Denomination.HEARTS] == 6
    assert data.makeable_tricks[Position.NORTH][Denomination.SPADES] == 6
    assert data.makeable_tricks[Position.NORTH][Denomination.NO_TRUMP] == 6

    assert data.makeable_tricks[Position.SOUTH][Denomination.HEARTS] == 6

    assert data.makeable_tricks[Position.EAST][Denomination.CLUBS] is None
    assert data.makeable_tricks[Position.WEST][Denomination.NO_TRUMP] is None


# ---------------------------------------------------------------------------
# Example 2 tests
# ---------------------------------------------------------------------------

def test_parse_bbo_hand_16_dealer_and_vulnerability() -> None:
    data = parse_bbo_html(BBO_HAND_16_HTML)

    assert data.dealer == Position.WEST
    assert data.vulnerability is Vulnerability.EAST_WEST


def test_parse_bbo_hand_16_each_hand_has_13_cards() -> None:
    data = parse_bbo_html(BBO_HAND_16_HTML)

    assert len(data.hands[Position.NORTH]) == 13
    assert len(data.hands[Position.SOUTH]) == 13
    assert len(data.hands[Position.EAST]) == 13
    assert len(data.hands[Position.WEST]) == 13


def test_parse_bbo_hand_16_north_hand() -> None:
    data = parse_bbo_html(BBO_HAND_16_HTML)

    expected = [
        card(Rank.TEN, Suit.SPADES),
        card(Rank.EIGHT, Suit.SPADES),
        card(Rank.TWO, Suit.SPADES),

        card(Rank.QUEEN, Suit.HEARTS),
        card(Rank.JACK, Suit.HEARTS),
        card(Rank.TWO, Suit.HEARTS),

        card(Rank.JACK, Suit.DIAMONDS),
        card(Rank.TEN, Suit.DIAMONDS),
        card(Rank.EIGHT, Suit.DIAMONDS),
        card(Rank.SIX, Suit.DIAMONDS),

        card(Rank.QUEEN, Suit.CLUBS),
        card(Rank.THREE, Suit.CLUBS),
        card(Rank.TWO, Suit.CLUBS),
    ]

    assert set(data.hands[Position.NORTH]) == set(expected)


def test_parse_bbo_hand_16_east_hand() -> None:
    data = parse_bbo_html(BBO_HAND_16_HTML)

    expected = [
        card(Rank.KING, Suit.SPADES),
        card(Rank.QUEEN, Suit.SPADES),
        card(Rank.SIX, Suit.SPADES),
        card(Rank.FIVE, Suit.SPADES),

        card(Rank.ACE, Suit.HEARTS),
        card(Rank.TEN, Suit.HEARTS),
        card(Rank.NINE, Suit.HEARTS),
        card(Rank.SEVEN, Suit.HEARTS),

        card(Rank.NINE, Suit.DIAMONDS),

        card(Rank.JACK, Suit.CLUBS),
        card(Rank.TEN, Suit.CLUBS),
        card(Rank.SEVEN, Suit.CLUBS),
        card(Rank.FIVE, Suit.CLUBS),
    ]

    assert set(data.hands[Position.EAST]) == set(expected)


def test_parse_bbo_hand_16_makeable_tricks() -> None:
    data = parse_bbo_html(BBO_HAND_16_HTML)

    assert data.makeable_tricks[Position.NORTH][Denomination.CLUBS] is None
    assert data.makeable_tricks[Position.NORTH][Denomination.NO_TRUMP] is None

    assert data.makeable_tricks[Position.EAST][Denomination.CLUBS] == 3
    assert data.makeable_tricks[Position.EAST][Denomination.DIAMONDS] == 2
    assert data.makeable_tricks[Position.EAST][Denomination.HEARTS] == 2
    assert data.makeable_tricks[Position.EAST][Denomination.SPADES] == 3
    assert data.makeable_tricks[Position.EAST][Denomination.NO_TRUMP] == 2


# ---------------------------------------------------------------------------
# Full-deal validation
# ---------------------------------------------------------------------------

def test_bbo_game_20_contains_all_52_unique_cards() -> None:
    data = parse_bbo_html(BBO_GAME_20_HTML)

    all_cards = []

    for hand in data.hands.values():
        all_cards.extend(hand)

    assert len(all_cards) == 52
    assert len(set(all_cards)) == 52

    expected_deck = {
        Card(rank, suit)
        for suit in Suit
        for rank in Rank
    }

    assert set(all_cards) == expected_deck


def test_bbo_hand_16_contains_all_52_unique_cards() -> None:
    data = parse_bbo_html(BBO_HAND_16_HTML)

    all_cards = []

    for hand in data.hands.values():
        all_cards.extend(hand)

    assert len(all_cards) == 52
    assert len(set(all_cards)) == 52

    expected_deck = {
        Card(rank, suit)
        for suit in Suit
        for rank in Rank
    }

    assert set(all_cards) == expected_deck


# ---------------------------------------------------------------------------
# Invalid input tests
# ---------------------------------------------------------------------------

def test_bbo_parser_requires_dealer() -> None:
    html = BBO_GAME_20_HTML.replace(
        '<abbr title="Dealer" class="has_tooltip">D</abbr>',
        "",
    )

    with pytest.raises(ValueError, match="dealer"):
        parse_bbo_html(html)


def test_bbo_parser_rejects_invalid_hand_size() -> None:
    html = BBO_GAME_20_HTML.replace(
        "<li>K</li><li>2</li>",
        "<li>K</li>",
        1,
    )

    with pytest.raises(ValueError, match="13"):
        parse_bbo_html(html)


def test_bbo_parser_rejects_duplicate_cards() -> None:
    html = BBO_GAME_20_HTML.replace(
        "<li>10</li><li>6</li><li>3</li>",
        "<li>K</li><li>6</li><li>3</li>",
        1,
    )

    with pytest.raises(ValueError, match="duplicate"):
        parse_bbo_html(html)


def test_bbo_parser_rejects_invalid_makeable_tricks_value() -> None:
    html = BBO_GAME_20_HTML.replace(
        '<td class="text_center">6</td>',
        '<td class="text_center">14</td>',
        1,
    )

    with pytest.raises(ValueError, match="makeable"):
        parse_bbo_html(html)


# ---------------------------------------------------------------------------
# Actual BBO example files
# ---------------------------------------------------------------------------

BBO_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "bbo"
)


def test_game_20_bbo_file_exists() -> None:
    path = BBO_DIRECTORY / "25-07-2026-game20.txt"

    assert path.is_file(), f"BBO example file not found: {path}"


def test_hand_16_bbo_file_exists() -> None:
    path = BBO_DIRECTORY / "260725-hand16.txt"

    assert path.is_file(), f"BBO example file not found: {path}"


def test_parse_game_20_bbo_file() -> None:
    path = BBO_DIRECTORY / "25-07-2026-game20.txt"

    game = parse_bbo_file(path)

    assert game.dealer == Position.WEST
    assert game.vulnerability == Vulnerability.BOTH

    assert all(
        len(hand) == 13
        for hand in game.hands.values()
    )

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


def test_parse_hand_16_bbo_file() -> None:
    path = BBO_DIRECTORY / "260725-hand16.txt"

    game = parse_bbo_file(path)

    assert game.dealer == Position.WEST
    assert game.vulnerability == Vulnerability.EAST_WEST

    assert all(
        len(hand) == 13
        for hand in game.hands.values()
    )

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