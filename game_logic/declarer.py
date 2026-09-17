"""
Determines the declarer and opening leader after bidding

The declarer is the first player from the partnership that won 
the auction who bid the denomination of the final contract

The opening leader is the player immediately to the left of the declarer.
"""

from bidding.bidding_system import BiddingSystem
from bidding.bid import Bid
from card_model.player import Position
from card_model.deck import seating_order_from

def determine_declarer(
        bidding_system: BiddingSystem, 
) -> Position | None:

    final_bid = bidding_system.highest_bid

    #A passed-out auction has no declarer
    if final_bid is None:
        return None

    final_bidder = None

    for position, bid in bidding_system.history:
        if bid == final_bid:
            final_bidder = position

    if final_bidder is None:
        return None

    #find first player from partnership who named denomination of final contract
    for position, bid in bidding_system.history:
        if not isinstance(bid, Bid):
            continue

        if bid.denomination != final_bid.denomination:
            continue

        if (
            position == final_bidder or position.partner == final_bidder
        ):
            return position

    return final_bidder

def determine_opening_leader(
        declarer: Position | None
) -> Position | None:

    #passed out auction has no declarer therefore no opening leader
    if declarer is None:
        return None

    opening_leader = {
        Position.NORTH: Position.EAST,
        Position.EAST: Position.SOUTH,
        Position.SOUTH: Position.WEST,
        Position.WEST: Position.NORTH,
    }

    return opening_leader[declarer]

def determine_next_player(
        current_player: Position
) -> Position:

    turn_order = seating_order_from(current_player)

    return turn_order[1]

