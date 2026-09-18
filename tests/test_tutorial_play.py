import pytest
from pathlib import Path

from card_model.card import Card, Rank, Suit
from card_model.player import Position
from bidding.bid import Denomination
from game_logic.lesson import LessonState
from game_logic.tutorial_play import (
    parse_play_card,
    parse_trick_line,
    determine_trick_winner,
    build_play_script,
    build_mode_one_lesson,
)
from game_logic.tutorial_parser import (
    parse_bid_and_play_lessons,
)


def test_parse_play_card():
    card = parse_play_card("8S")

    assert card == Card(
        Rank.EIGHT,
        Suit.SPADES,
    )


def test_parse_play_ten():
    card = parse_play_card("TH")

    assert card == Card(
        Rank.TEN,
        Suit.HEARTS,
    )


def test_invalid_play_card_is_rejected():
    with pytest.raises(ValueError):
        parse_play_card("8X")


def test_parse_trick_from_west():
    trick = parse_trick_line(
        "8S,TS,9S,3S",
        Position.WEST,
    )

    assert trick == [
        (
            Position.WEST,
            Card(Rank.EIGHT, Suit.SPADES),
        ),
        (
            Position.NORTH,
            Card(Rank.TEN, Suit.SPADES),
        ),
        (
            Position.EAST,
            Card(Rank.NINE, Suit.SPADES),
        ),
        (
            Position.SOUTH,
            Card(Rank.THREE, Suit.SPADES),
        ),
    ]


def test_parse_trick_from_south():
    trick = parse_trick_line(
        "AS,2S,4S,9S",
        Position.SOUTH,
    )

    assert trick[0][0] == Position.SOUTH
    assert trick[1][0] == Position.WEST
    assert trick[2][0] == Position.NORTH
    assert trick[3][0] == Position.EAST


def test_trick_requires_four_cards():
    with pytest.raises(ValueError):
        parse_trick_line(
            "AS,KS,QS",
            Position.SOUTH,
        )

def test_highest_card_of_led_suit_wins():
    trick = parse_trick_line(
        "8S,TS,9S,3S",
        Position.WEST,
    )

    winner = determine_trick_winner(
        trick,
        trump_suit=None,
    )

    assert winner == Position.NORTH


def test_off_suit_card_cannot_win():
    trick = parse_trick_line(
        "8S,2H,AS,KS",
        Position.WEST,
    )

    winner = determine_trick_winner(
        trick,
        trump_suit=None,
    )

    assert winner == Position.EAST


def test_trump_beats_led_suit():
    trick = parse_trick_line(
        "AD,2D,KD,2S",
        Position.WEST,
    )

    winner = determine_trick_winner(
        trick,
        trump_suit=Suit.SPADES,
    )

    assert winner == Position.SOUTH


def test_highest_trump_wins():
    trick = parse_trick_line(
        "AD,2S,KD,QS",
        Position.WEST,
    )

    winner = determine_trick_winner(
        trick,
        trump_suit=Suit.SPADES,
    )

    assert winner == Position.SOUTH

def test_build_play_script_updates_leader():
    raw_play_lines = [
        "8S,TS,9S,3S",
        "4C,9C,QC,3C",
    ]

    script = build_play_script(
        raw_play_lines,
        opening_leader=Position.WEST,
        trump_suit=None,
    )

    assert len(script) == 8

    # Trick 1 begins with West.
    assert script[0] == (
        Position.WEST,
        Card(Rank.EIGHT, Suit.SPADES),
    )

    # North wins trick 1 with TS,
    # so North leads trick 2 with 4C.
    assert script[4] == (
        Position.NORTH,
        Card(Rank.FOUR, Suit.CLUBS),
    )


def test_build_full_first_sonia_play_script():
    raw_play_lines = [
        "8S,TS,9S,3S",
        "4C,9C,QC,3C",
        "8C,7C,2C,TC",
        "4S,KS,7S,JS",
        "KH,4H,3H,TH",
        "8H,9H,AH,2H",
        "QH,2S,6H,7H",
        "6D,3D,AD,5D",
        "2D,8D,JD,4D",
    ]

    script = build_play_script(
        raw_play_lines,
        opening_leader=Position.WEST,
        trump_suit=None,
    )

    # Sonia supplies 9 complete tricks.
    assert len(script) == 36

    assert script[0] == (
        Position.WEST,
        Card(Rank.EIGHT, Suit.SPADES),
    )

    assert script[-1] == (
        Position.EAST,
        Card(Rank.FOUR, Suit.DIAMONDS),
    )


def test_empty_play_lines_produce_empty_script():
    script = build_play_script(
        [],
        opening_leader=Position.WEST,
        trump_suit=None,
    )

    assert script == []

def test_build_mode_one_lesson_from_real_sponsor_data():
    fixture_path = (
        Path(__file__).parent
        / "lessons"
        / "exampleBidAndPlay.txt"
    )

    lessons = parse_bid_and_play_lessons(
        fixture_path.read_text()
    )

    lesson = build_mode_one_lesson(
        lessons[0]
    )

    assert lesson.dealer == Position.SOUTH

    assert lesson.contract.bid.level == 6
    assert (
        lesson.contract.bid.denomination
        == Denomination.NO_TRUMP
    )

    assert lesson.contract.declarer == Position.SOUTH
    assert lesson.opening_leader == Position.WEST

    assert lesson.contract.trump_suit is None

    assert lesson.user_seats == frozenset({
        Position.NORTH,
        Position.SOUTH,
    })

    # 9 prescribed tricks before Claim.
    assert len(lesson.script) == 36

def test_mode_one_uses_south_as_declarer_and_west_as_opening_leader():
    fixture_path = (
        Path(__file__).parent
        / "lessons"
        / "exampleBidAndPlay.txt"
    )

    data = parse_bid_and_play_lessons(
        fixture_path.read_text()
    )

    # Mode 1 lessons always use South as declarer,
    # so West must be the opening leader.
    lesson = build_mode_one_lesson(data[0])

    assert lesson.contract.declarer == Position.SOUTH
    assert lesson.opening_leader == Position.WEST


def test_real_sponsor_lesson_runs_through_lesson_state():
    fixture_path = (
        Path(__file__).parent
        / "lessons"
        / "exampleBidAndPlay.txt"
    )

    data = parse_bid_and_play_lessons(
        fixture_path.read_text()
    )[0]

    lesson = build_mode_one_lesson(data)
    state = LessonState(lesson)

    for position, card in lesson.script:
        assert state.attempt_play(
            position,
            card,
        )

    assert state.is_complete()
    assert state.mistake_count == 0

def test_all_real_sponsor_lessons_build_successfully():
    fixture_path = (
        Path(__file__).parent
        / "lessons"
        / "exampleBidAndPlay.txt"
    )

    data = parse_bid_and_play_lessons(
        fixture_path.read_text()
    )

    assert len(data) == 3

    for tutorial_data in data:
        lesson = build_mode_one_lesson(
            tutorial_data
        )

        assert len(lesson.script) > 0

        state = LessonState(lesson)

        for position, card in lesson.script:
            assert state.attempt_play(
                position,
                card,
            )

        assert state.is_complete()
        assert state.mistake_count == 0

def test_game_three_real_sponsor_lesson_builds_successfully():
    fixture_path = (
        Path(__file__).parent
        / "lessons"
        / "exampleBidAndPlay.txt"
    )

    lessons = parse_bid_and_play_lessons(
        fixture_path.read_text()
    )

    # Game 3 is the third lesson in the sponsor file.
    data = lessons[2]

    lesson = build_mode_one_lesson(data)

    state = LessonState(lesson)

    for position, card in lesson.script:
        assert state.attempt_play(position, card)

    assert state.is_complete()
    assert state.mistake_count == 0