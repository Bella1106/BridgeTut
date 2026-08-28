from bidding.bid import Bid, Denomination
from bidding.bidding_system import BiddingSystem
from card_model.player import Position
import pytest

def test_first_bid_accepted():
    system = BiddingSystem(Position.SOUTH)
    bid = Bid(1, Denomination.CLUBS)

    result = system.make_bid(Position.SOUTH, bid)

    assert result is True
    assert system.highest_bid == bid

def test_higher_denomination_accepted():
    "tests 1H -> 1S accepts"
    system = BiddingSystem(Position.SOUTH)

    system.make_bid(Position.SOUTH, Bid(1, Denomination.HEARTS))

    higher_bid = Bid(1, Denomination.SPADES)

    assert system.make_bid(Position.WEST, higher_bid) is True
    assert system.highest_bid == higher_bid

def test_higher_level_accepted():
    "tests 1NT -> 2C is accepted"
    system = BiddingSystem(Position.SOUTH)
    
    system.make_bid(Position.SOUTH, Bid(1, Denomination.NO_TRUMP))
    
    higher_bid = Bid(2, Denomination.CLUBS)

    assert system.make_bid(Position.WEST, higher_bid) is True
    assert system.highest_bid == higher_bid

def test_lower_bid_rejected():
    "proving rejection didn't accidentally change highest_bid"
    system = BiddingSystem(Position.SOUTH)

    original_bid = Bid(2, Denomination.HEARTS)
    system.make_bid(Position.SOUTH, original_bid)

    lower_bid = Bid(2, Denomination.DIAMONDS)

    assert system.make_bid(Position.WEST, lower_bid) is False
    assert system.highest_bid == original_bid

def test_equal_bid_rejected():
    "proves you cannot just repeat someone elses bid"
    system = BiddingSystem(Position.SOUTH)

    original_bid = Bid(2, Denomination.HEARTS)
    system.make_bid(Position.SOUTH, original_bid)

    same_bid = Bid(2, Denomination.HEARTS)

    assert system.make_bid(Position.WEST, same_bid) is False
    assert system.highest_bid == original_bid

def test_accepted_bid_recorded():
    system = BiddingSystem(Position.SOUTH)
    bid = Bid(1, Denomination.CLUBS)

    system.make_bid(Position.SOUTH, bid)

    assert system.history == [(Position.SOUTH, bid)]

def test_rejected_bid_not_recorded():
    "checks history represents legal auction and not just all bids"
    system = BiddingSystem(Position.SOUTH)

    accepted_bid = Bid(2, Denomination.HEARTS)
    rejected_bid = Bid(2, Denomination.CLUBS)

    system.make_bid(Position.SOUTH, accepted_bid)
    system.make_bid(Position.WEST, rejected_bid)

    assert system.history == [(Position.SOUTH, accepted_bid)]

def test_history_preserves_bid_order():
    system = BiddingSystem(Position.SOUTH)
    
    first = Bid(1, Denomination.CLUBS)
    second = Bid(1, Denomination.HEARTS)
    third = Bid(2, Denomination.CLUBS)

    system.make_bid(Position.SOUTH, first)
    system.make_bid(Position.WEST, second)
    system.make_bid(Position.NORTH, third)
    
    assert system.history == [
        (Position.SOUTH, first),
        (Position.WEST, second),
        (Position.NORTH, third),
        ]

def test_invalid_player_type_rejected():
    system =  BiddingSystem(Position.SOUTH)
    bid = Bid(1, Denomination.CLUBS)

    with pytest.raises(TypeError):
        system.make_bid("South", bid)
        "architecture says SOUTH bot south"

def test_dealer_starts_bidding():
    system = BiddingSystem(Position.NORTH)

    assert system.current_player == Position.NORTH

def test_turn_advances_after_valid_bid():
    system = BiddingSystem(Position.SOUTH)

    system.make_bid(Position.SOUTH, Bid(1, Denomination.CLUBS))

    assert system.current_player == Position.WEST

def test_turn_wraps_around_clockwise():
    system = BiddingSystem(Position.EAST)

    system.make_bid(Position.EAST, Bid(1, Denomination.CLUBS))

    assert system.current_player == Position.SOUTH

def test_out_of_turn_bid_rejected():
    system = BiddingSystem(Position.SOUTH)
    bid = Bid(1, Denomination.CLUBS)

    result = system.make_bid(Position.NORTH, bid)

    assert result is False
    assert system.history == []
    assert system.current_player == Position.SOUTH

def test_pass_accepted_and_recorded():
    system = BiddingSystem(Position.SOUTH)

    result = system.make_pass(Position.SOUTH)

    assert result is True
    assert system.history == [(Position.SOUTH, None)]

def test_pass_advances_turn():
    system = BiddingSystem(Position.SOUTH)

    system.make_pass(Position.SOUTH)

    assert system.current_player == Position.WEST

def test_consecutive_passes_are_counted():
    system = BiddingSystem(Position.SOUTH)

    system.make_pass(Position.SOUTH)
    system.make_pass(Position.WEST)

    assert system.consecutive_passes == 2

def test_bid_resets_consecutive_passes():
    system = BiddingSystem(Position.SOUTH)

    system.make_pass(Position.SOUTH)
    system.make_pass(Position.WEST)

    system.make_bid(Position.NORTH, Bid(1, Denomination.CLUBS))

    assert system.consecutive_passes == 0

def test_three_passes_after_bid_end_auction():
    system = BiddingSystem(Position.SOUTH)

    bid = Bid(1, Denomination.HEARTS)

    system.make_bid(Position.SOUTH, bid)
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    assert system.auction_finished is True
    assert system.highest_bid == bid

def test_history_preserved():
    system = BiddingSystem(Position.SOUTH)

    bid = Bid(1, Denomination.HEARTS)

    system.make_bid(Position.SOUTH, bid)
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    assert system.history == [
        (Position.SOUTH, bid),
        (Position.WEST, None),
        (Position.NORTH, None),
        (Position.EAST, None),
    ]

def test_bid_after_auction_finished_rejected():
    system = BiddingSystem(Position.SOUTH)
        
    system.make_bid(Position.SOUTH, Bid(1, Denomination.HEARTS))
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    result = system.make_bid(Position.SOUTH, Bid(1, Denomination.SPADES))

    assert result is False

def test_pass_after_auction_finished_rejected():
    system = BiddingSystem(Position.SOUTH)
    
    system.make_bid(Position.SOUTH, Bid(1, Denomination.HEARTS))
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    result = system.make_pass(Position.SOUTH)

    assert result is False

def test_invalid_player_cannot_pass():
    system = BiddingSystem(Position.SOUTH)

    with pytest.raises(TypeError):
        system.make_pass("South")

"post gui merge tests to cover potential gaps"
def test_invalid_bid_type_rejected():
    system = BiddingSystem(Position.SOUTH)


    with pytest.raises(TypeError):
        system.make_bid(Position.SOUTH, "1H")

def test_rejected_bid_does_not_change_auction_state():
    system = BiddingSystem(Position.SOUTH)

    original_bid = Bid(2, Denomination.HEARTS)
    system.make_bid(Position.SOUTH, original_bid)

    original_history = system.history.copy()
    original_player = system.current_player
    original_passes = system.consecutive_passes

    result = system.make_bid(Position.WEST, Bid(2, Denomination.CLUBS))

    assert result is False
    assert system.highest_bid == original_bid
    assert system.history == original_history
    assert system.current_player == original_player
    assert system.consecutive_passes == original_passes
    assert system.auction_finished is False

def test_out_of_turn_pass_rejected_without_state_change():
    system = BiddingSystem(Position.SOUTH)

    result = system.make_pass(Position.NORTH)

    assert result is False
    assert system.history == []
    assert system.current_player == Position.SOUTH
    assert system.consecutive_passes == 0
    assert system.auction_finished is False

def test_seven_no_trump_valid_highest_bid():
    system = BiddingSystem(Position.SOUTH)
    highest_possible_bid = Bid(7, Denomination.NO_TRUMP)

    result = system.make_bid(Position.SOUTH, highest_possible_bid)

    assert result is True
    assert system.highest_bid == highest_possible_bid

def test_no_contract_bid_can_outrank_seven_no_trump():
    system = BiddingSystem(Position.SOUTH)

    system.make_bid(Position.SOUTH, Bid(7, Denomination.NO_TRUMP))

    for level in range(1,8):
        for denomination in Denomination:
            assert system.is_valid_bid(Bid(level, denomination)) is False

def test_mixed_auction_sequence():
    system = BiddingSystem(Position.SOUTH)

    one_club = Bid(1, Denomination.CLUBS)
    one_heart = Bid(1, Denomination.HEARTS)
    two_clubs = Bid(2, Denomination.CLUBS)

    assert system.make_bid(Position.SOUTH, one_club) is True
    assert system.make_pass(Position.WEST) is True
    assert system.make_bid(Position.NORTH, one_heart) is True
    assert system.make_bid(Position.EAST, two_clubs) is True
    assert system.make_pass(Position.SOUTH) is True
    assert system.make_pass(Position.WEST) is True
    assert system.make_pass(Position.NORTH) is True

    assert system.auction_finished is True
    assert system.highest_bid == two_clubs
    assert system.consecutive_passes == 3

    assert system.history == [
        (Position.SOUTH, one_club),
        (Position.WEST, None),
        (Position.NORTH, one_heart),
        (Position.EAST, two_clubs),
        (Position.SOUTH, None),
        (Position.WEST, None),
        (Position.NORTH, None),
    ]

def test_three_opening_passes_do_not_end_auction():
    system = BiddingSystem(Position.SOUTH)

    system.make_pass(Position.SOUTH)
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)

    assert system.auction_finished is False
    assert system.highest_bid is None

def test_four_opening_passes_end_auction_as_passed_out():
    system = BiddingSystem(Position.SOUTH)

    system.make_pass(Position.SOUTH)
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    assert system.auction_finished is True
    assert system.highest_bid is None
    assert system.consecutive_passes == 4