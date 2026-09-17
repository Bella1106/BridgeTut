import pytest

from bidding.bid import Bid, Denomination
from card_model.card import Card, Rank, Suit
from card_model.deck import Deck
from card_model.player import Position
from contract.contract import Contract

from game_logic.lesson import Lesson, LessonState

def _hands_and_script():
    """A fixed, legal deal plus a script that plays every hand out
    top-down by suit -- not a realistic line of play, just something
    exact and easy to assert against.
    """
    cards = Deck(seed=3).cards
    positions = [Position.NORTH, Position.EAST, Position.SOUTH, Position.WEST]

    hands = {
        position: cards[i * 13:(i + 1) * 13]
        for i, position in enumerate(positions)
    }

    order = [Position.SOUTH, Position.WEST, Position.NORTH, Position.EAST]

    script = []

    for round_index in range(13):
        for position in order:
            script.append((position, hands[position][round_index]))

    return hands, script

def _lesson(user_seats=frozenset({Position.NORTH, Position.SOUTH})):
    hands, script = _hands_and_script()

    contract = Contract(
        bid=Bid(4, Denomination.HEARTS),
        declarer=Position.SOUTH,
    )

    return Lesson(
        dealer=Position.SOUTH,
        hands=hands,
        contract=contract,
        opening_leader=Position.WEST,
        script=script,
        user_seats=user_seats,
    )

# =====================================================
# LESSON VALIDATION
# =====================================================

def test_valid_lesson_constructs_without_error():
    _lesson()

def test_lesson_missing_a_hand_raises():
    hands, script = _hands_and_script()
    del hands[Position.WEST]

    with pytest.raises(ValueError):
        Lesson(
            dealer=Position.SOUTH,
            hands=hands,
            contract=Contract(Bid(4, Denomination.HEARTS), Position.SOUTH),
            opening_leader=Position.WEST,
            script=script,
            user_seats=frozenset({Position.NORTH, Position.SOUTH}),
        )

def test_lesson_short_script_raises():
    hands, script = _hands_and_script()

    with pytest.raises(ValueError):
        Lesson(
            dealer=Position.SOUTH,
            hands=hands,
            contract=Contract(Bid(4, Denomination.HEARTS), Position.SOUTH),
            opening_leader=Position.WEST,
            script=script[:-1],
            user_seats=frozenset({Position.NORTH, Position.SOUTH}),
        )

def test_lesson_script_not_matching_a_hand_raises():
    hands, script = _hands_and_script()

    # Swap one of North's scripted cards for a card North never held.
    other_card = hands[Position.EAST][0]
    bad_script = list(script)
    position, _ = bad_script[0]
    bad_script[0] = (position, other_card)

    with pytest.raises(ValueError):
        Lesson(
            dealer=Position.SOUTH,
            hands=hands,
            contract=Contract(Bid(4, Denomination.HEARTS), Position.SOUTH),
            opening_leader=Position.WEST,
            script=bad_script,
            user_seats=frozenset({Position.NORTH, Position.SOUTH}),
        )

# =====================================================
# LESSON STATE: HAPPY PATH
# =====================================================

def test_current_player_and_expected_card_follow_the_script():
    lesson = _lesson()
    state = LessonState(lesson)

    expected_position, expected_card = lesson.script[0]

    assert state.current_player == expected_position
    assert state.expected_card == expected_card

def test_correct_play_advances_the_script():
    lesson = _lesson()
    state = LessonState(lesson)

    position, card = lesson.script[0]

    assert state.attempt_play(position, card) is True
    assert state.step == 1
    assert state.plays_made == [(position, card)]

def test_playing_all_52_completes_the_lesson():
    lesson = _lesson()
    state = LessonState(lesson)

    for position, card in lesson.script:
        assert state.attempt_play(position, card) is True

    assert state.is_complete()
    assert state.current_player is None
    assert state.expected_card is None

def test_no_mistakes_recorded_on_a_perfect_run():
    lesson = _lesson()
    state = LessonState(lesson)

    for position, card in lesson.script:
        state.attempt_play(position, card)

    assert state.mistake_count == 0

# =====================================================
# LESSON STATE: MISTAKES
# =====================================================

def test_wrong_card_is_rejected_and_does_not_advance():
    lesson = _lesson()
    state = LessonState(lesson)

    position, _ = lesson.script[0]
    wrong_card = lesson.script[1][1]

    assert state.attempt_play(position, wrong_card) is False
    assert state.step == 0

def test_wrong_card_is_recorded_as_a_mistake():
    lesson = _lesson()
    state = LessonState(lesson)

    position, correct_card = lesson.script[0]
    wrong_card = lesson.script[1][1]

    state.attempt_play(position, wrong_card)

    assert state.mistake_count == 1

    mistake = state.mistakes[0]

    assert mistake.step == 0
    assert mistake.position == position
    assert mistake.expected_card == correct_card
    assert mistake.attempted_card == wrong_card

def test_a_mistake_does_not_stop_a_later_correct_attempt():
    lesson = _lesson()
    state = LessonState(lesson)

    position, correct_card = lesson.script[0]
    wrong_card = lesson.script[1][1]

    state.attempt_play(position, wrong_card)

    assert state.attempt_play(position, correct_card) is True
    assert state.step == 1

def test_play_after_lesson_complete_is_rejected():
    lesson = _lesson()
    state = LessonState(lesson)

    for position, card in lesson.script:
        state.attempt_play(position, card)

    last_position, last_card = lesson.script[-1]

    assert state.attempt_play(last_position, last_card) is False

# =====================================================
# SEAT CONTROL
# =====================================================

def test_is_user_turn_true_for_user_seats():
    lesson = _lesson(user_seats=frozenset({Position.NORTH, Position.SOUTH}))
    state = LessonState(lesson)

    while not state.is_complete():
        position, card = lesson.script[state.step]
        expected_user_turn = position in (Position.NORTH, Position.SOUTH)

        assert state.is_user_turn() == expected_user_turn

        state.attempt_play(position, card)
