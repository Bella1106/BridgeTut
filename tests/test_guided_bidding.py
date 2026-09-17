from bidding.bid import Bid, Denomination
from bidding.bidding_system import SpecialCall
from card_model.player import Position
from game_logic.guided_bidding import (
    GuidedBiddingLesson,
    GuidedBiddingState,
)

# =====================================================
# BASIC GUIDED BIDDING
# =====================================================

def test_guided_bidding_starts_with_dealer():
    lesson = GuidedBiddingLesson(
        dealer=Position.SOUTH,
        script=[
            (
                Position.SOUTH,
                Bid(1, Denomination.HEARTS),
            ),
        ],
    )

    state = GuidedBiddingState(lesson)

    assert state.current_player == Position.SOUTH
    assert state.expected_call == Bid(
        1,
        Denomination.HEARTS,
    )
    assert state.step == 0


def test_correct_user_bid_is_accepted():
    bid = Bid(1, Denomination.HEARTS)

    lesson = GuidedBiddingLesson(
        dealer=Position.SOUTH,
        script=[
            (Position.SOUTH, bid),
        ],
    )

    state = GuidedBiddingState(lesson)

    result = state.attempt_call(
        Position.SOUTH,
        bid,
    )

    assert result is True
    assert state.calls_made == [
        (Position.SOUTH, bid)
    ]
    assert state.step == 1
    assert state.is_complete()


def test_wrong_user_bid_is_rejected():
    expected = Bid(1, Denomination.HEARTS)
    attempted = Bid(1, Denomination.SPADES)

    lesson = GuidedBiddingLesson(
        dealer=Position.SOUTH,
        script=[
            (Position.SOUTH, expected),
        ],
    )

    state = GuidedBiddingState(lesson)

    result = state.attempt_call(
        Position.SOUTH,
        attempted,
    )

    assert result is False
    assert state.step == 0
    assert state.expected_call == expected
    assert state.mistake_count == 1


def test_wrong_bid_records_mistake():
    expected = Bid(1, Denomination.HEARTS)
    attempted = Bid(1, Denomination.SPADES)

    lesson = GuidedBiddingLesson(
        dealer=Position.SOUTH,
        script=[
            (Position.SOUTH, expected),
        ],
    )

    state = GuidedBiddingState(lesson)

    state.attempt_call(
        Position.SOUTH,
        attempted,
    )

    mistake = state.mistakes[0]

    assert mistake.step == 0
    assert mistake.position == Position.SOUTH
    assert mistake.expected_call == expected
    assert mistake.attempted_call == attempted


# =====================================================
# COMPUTER-CONTROLLED BIDDING
# =====================================================

def test_computer_calls_stop_at_south():
    expected_south_bid = Bid(
        1,
        Denomination.SPADES,
    )

    lesson = GuidedBiddingLesson(
        dealer=Position.NORTH,
        script=[
            (Position.NORTH, None),
            (Position.EAST, None),
            (Position.SOUTH, expected_south_bid),
        ],
    )

    state = GuidedBiddingState(lesson)

    state.play_computer_calls()

    assert state.calls_made == [
        (Position.NORTH, None),
        (Position.EAST, None),
    ]

    assert state.current_player == Position.SOUTH
    assert state.expected_call == expected_south_bid
    assert state.is_user_turn()


def test_computer_calls_continue_after_correct_south_bid():
    south_bid = Bid(
        1,
        Denomination.SPADES,
    )

    north_bid = Bid(
        1,
        Denomination.NO_TRUMP,
    )

    lesson = GuidedBiddingLesson(
        dealer=Position.NORTH,
        script=[
            (Position.NORTH, None),
            (Position.EAST, None),
            (Position.SOUTH, south_bid),
            (Position.WEST, None),
            (Position.NORTH, north_bid),
            (Position.EAST, None),
        ],
    )

    state = GuidedBiddingState(lesson)

    state.play_computer_calls()

    assert state.current_player == Position.SOUTH

    assert state.attempt_call(
        Position.SOUTH,
        south_bid,
    )

    state.play_computer_calls()

    assert state.calls_made == lesson.script
    assert state.is_complete()

# =====================================================
# SONIA BID + PLAY EXAMPLE
# =====================================================

def test_sonia_bid_and_play_auction():
    one_spade = Bid(
        1,
        Denomination.SPADES,
    )

    one_nt = Bid(
        1,
        Denomination.NO_TRUMP,
    )

    three_spades = Bid(
        3,
        Denomination.SPADES,
    )

    four_spades = Bid(
        4,
        Denomination.SPADES,
    )

    lesson = GuidedBiddingLesson(
        dealer=Position.NORTH,
        script=[
            (Position.NORTH, None),
            (Position.EAST, None),
            (Position.SOUTH, one_spade),
            (Position.WEST, None),
            (Position.NORTH, one_nt),
            (Position.EAST, None),
            (Position.SOUTH, three_spades),
            (Position.WEST, None),
            (Position.NORTH, four_spades),
        ],
    )

    state = GuidedBiddingState(lesson)

    # N and E bid automatically.
    state.play_computer_calls()

    assert state.current_player == Position.SOUTH
    assert state.expected_call == one_spade

    # South makes the correct prescribed bid.
    assert state.attempt_call(
        Position.SOUTH,
        one_spade,
    )

    # W, N and E continue automatically.
    state.play_computer_calls()

    assert state.current_player == Position.SOUTH
    assert state.expected_call == three_spades

    # South makes the next prescribed bid.
    assert state.attempt_call(
        Position.SOUTH,
        three_spades,
    )

    # Remaining scripted calls are automatic.
    state.play_computer_calls()

    assert state.is_complete()
    assert state.calls_made == lesson.script
    assert state.mistake_count == 0

def test_guided_bidding_supports_double():
    two_clubs = Bid(
        2,
        Denomination.CLUBS,
    )

    three_hearts = Bid(
        3,
        Denomination.HEARTS,
    )

    lesson = GuidedBiddingLesson(
        dealer=Position.SOUTH,
        script=[
            (Position.SOUTH, two_clubs),
            (Position.WEST, three_hearts),
            (Position.NORTH, SpecialCall.DOUBLE),
            (Position.EAST, None),
        ],
    )

    state = GuidedBiddingState(lesson)

    assert state.attempt_call(
        Position.SOUTH,
        two_clubs,
    )

    state.play_computer_calls()

    assert state.is_complete()

    assert (
        Position.NORTH,
        SpecialCall.DOUBLE,
    ) in state.calls_made

    assert (
        state.bidding_system.doubling_state
        == SpecialCall.DOUBLE
    )