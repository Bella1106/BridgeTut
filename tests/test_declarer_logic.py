from bidding.bid import Bid, Denomination
from bidding.bidding_system import BiddingSystem
from card_model.player import Position

from game_logic.declarer import (determine_declarer, determine_opening_leader, determine_next_player)

# =====================================================
# DECLARER TESTS
# =====================================================

def test_final_bidder_is_declarer_when_partner_did_not_bid_suit():
    system = BiddingSystem(Position.SOUTH)

    system.make_bid(Position.SOUTH, Bid(1, Denomination.CLUBS))
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    assert determine_declarer(system) == Position.SOUTH

def test_first_partner_to_bid_final_denomination_is_declarer():
    system = BiddingSystem(Position.SOUTH)

    system.make_bid(Position.SOUTH, Bid(1, Denomination.HEARTS))
    system.make_pass(Position.WEST)

    system.make_bid(Position.NORTH, Bid(2, Denomination.HEARTS))

    system.make_pass(Position.EAST)
    system.make_pass(Position.SOUTH)
    system.make_pass(Position.WEST)

    # North made the final bid, but South named
    # hearts first for the partnership.
    assert determine_declarer(system) == Position.SOUTH

def test_opponents_bid_same_denomination_does_not_change_declarer():
    system = BiddingSystem(Position.SOUTH)

    system.make_bid(Position.SOUTH, Bid(1, Denomination.HEARTS))

    system.make_bid(Position.WEST, Bid(1, Denomination.SPADES))

    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)
    system.make_pass(Position.SOUTH)

    assert determine_declarer(system) == Position.WEST

def test_passed_out_auction_has_no_declarer():
    system = BiddingSystem(Position.SOUTH)

    system.make_pass(Position.SOUTH)
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    assert determine_declarer(system) is None

# =====================================================
# OPENING LEADER TESTS
# =====================================================

def test_opening_leader_left_of_north():
    assert (determine_opening_leader(Position.NORTH) == Position.EAST)

def test_opening_leader_left_of_east():
    assert (determine_opening_leader(Position.EAST) == Position.SOUTH)

def test_opening_leader_left_of_south():
    assert (determine_opening_leader(Position.SOUTH) == Position.WEST)

def test_opening_leader_left_of_west():
    assert (determine_opening_leader(Position.WEST) == Position.NORTH)

def test_no_declarer_has_no_opening_leader():
    assert determine_opening_leader(None) is None

# =====================================================
# PLAY ORDER TESTS
# =====================================================

def test_next_player_after_south_is_west():
    assert (determine_opening_leader(Position.SOUTH) == Position.WEST)

def test_next_player_after_west_is_north():
    assert (determine_opening_leader(Position.WEST) == Position.NORTH)

def test_next_player_after_north_is_east():
    assert (determine_opening_leader(Position.NORTH) == Position.EAST)

def test_next_player_after_east_is_south():
    assert (determine_opening_leader(Position.EAST) == Position.SOUTH)

