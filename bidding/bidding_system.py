"""
Manages the bidding phase of a bridge game.

The bidding system validates calls against the current auction 
and records accepted calls in the bidding history.
"""
from bidding.bid import Bid
from card_model.player import Position

class BiddingSystem:
    "maintains the state and history of an auction"

    def __init__(self):
        self.history: list[tuple[Position, Bid]] = []
        self.highest_bid: Bid | None = None

    def is_valid_bid(self, bid: Bid) -> bool:
        if self.highest_bid is None:
            return True

        return bid > self.highest_bid

    def make_bid(self, player: Position, bid: Bid) -> bool:
        "attempt to make bid"
        "true -> bid accepted and recorded"
        "false -> bid does not outrank highest bid"

        if not isinstance(player, Position):
            raise TypeError("Player must be a Position")

        if not self.is_valid_bid(bid):
            return False

        self.history.append((player, bid))
        self.highest_bid = bid
        return True