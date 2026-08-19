from bidding.bid import Bid, Denomination
from bidding.bidding_system import BiddingSystem
from card_model.player import Position
import pytest

def test_first_bid_accepted():
    system = BiddingSystem()
    bid = Bid(1, Denomination.CLUBS)

    result = system.make_bid(Position.SOUTH, bid)

    assert result is True
    assert system.highest_bid == bid

def test_higher_denomination_accepted():
    "tests 1H -> 1S accepts"
    system = BiddingSystem()

    system.make_bid(Position.SOUTH, Bid(1, Denomination.HEARTS))

    higher_bid = Bid(1, Denomination.SPADES)

    assert system.make_bid(Position.WEST, higher_bid) is True
    assert system.highest_bid == higher_bid

def test_higher_level_accepted():
    "tests 1NT -> 2C is accepted"
    system = BiddingSystem()
    
    system.make_bid(Position.SOUTH, Bid(1, Denomination.NO_TRUMP))
    
    higher_bid = Bid(2, Denomination.CLUBS)

    assert system.make_bid(Position.WEST, higher_bid) is True
    assert system.highest_bid == higher_bid

def test_lower_bid_rejected():
    "proving rejection didn't accidentally change highest_bid"
    system = BiddingSystem()

    original_bid = Bid(2, Denomination.HEARTS)
    system.make_bid(Position.SOUTH, original_bid)

    lower_bid = Bid(2, Denomination.DIAMONDS)

    assert system.make_bid(Position.WEST, lower_bid) is False
    assert system.highest_bid == original_bid

def test_equal_bid_rejected():
    "proves you cannot just repeat someone elses bid"
    system = BiddingSystem()

    original_bid = Bid(2, Denomination.HEARTS)
    system.make_bid(Position.SOUTH, original_bid)

    same_bid = Bid(2, Denomination.HEARTS)

    assert system.make_bid(Position.WEST, same_bid) is False
    assert system.highest_bid == original_bid

def test_accepted_bid_recorded():
    system = BiddingSystem()
    bid = Bid(1, Denomination.CLUBS)

    system.make_bid(Position.SOUTH, bid)

    assert system.history == [(Position.SOUTH, bid)]

def test_rejected_bid_not_recorded():
    "checks history represents legal auction and not just all bids"
    system = BiddingSystem()

    accepted_bid = Bid(2, Denomination.HEARTS)
    rejected_bid = Bid(2, Denomination.CLUBS)

    system.make_bid(Position.SOUTH, accepted_bid)
    system.make_bid(Position.WEST, rejected_bid)

    assert system.history == [(Position.SOUTH, accepted_bid)]

def test_history_preserves_bid_order():
    system = BiddingSystem()
    
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
    system =  BiddingSystem()
    bid = Bid(1, Denomination.CLUBS)

    with pytest.raises(TypeError):
        system.make_bid("South", bid)
        "architecture says SOUTH bot south"