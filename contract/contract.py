"""
contract.py
-----------
Determines the final contract once an auction has finished.

A Contract is the outcome of the bidding phase: the winning bid, and
who plays it (the declarer). Trump suit / No Trump status are derived
from the winning bid's denomination rather than stored separately, so
they can never disagree with the bid itself.
"""

from __future__ import annotations
from dataclasses import dataclass

from bidding.bid import Bid, Denomination
from bidding.bidding_system import BiddingSystem
from card_model.card import Suit
from card_model.player import Position

_DENOMINATION_TO_TRUMP_SUIT = {
    Denomination.CLUBS: Suit.CLUBS,
    Denomination.DIAMONDS: Suit.DIAMONDS,
    Denomination.HEARTS: Suit.HEARTS,
    Denomination.SPADES: Suit.SPADES,
}


@dataclass(frozen=True)
class Contract:
    "the outcome of a finished, non-passed-out auction"

    bid: Bid
    declarer: Position

    @property
    def level(self) -> int:
        return self.bid.level

    @property
    def denomination(self) -> Denomination:
        return self.bid.denomination

    @property
    def is_no_trump(self) -> bool:
        return self.bid.denomination == Denomination.NO_TRUMP

    @property
    def trump_suit(self) -> Suit | None:
        "the trump suit for play, or None for a No Trump contract"
        return _DENOMINATION_TO_TRUMP_SUIT.get(self.bid.denomination)

    @property
    def dummy(self) -> Position:
        "declarer's partner -- hand is exposed during the Play phase"
        return self.declarer.partner

    def __repr__(self) -> str:
        return f"{self.bid} by {self.declarer}"


def determine_declarer(system: BiddingSystem) -> Position | None:
    """The declarer is the first player, from the partnership that won
    the auction, to have named the winning denomination -- not
    necessarily whoever made the final/highest bid.

    Returns None if no bid was ever made (auction passed out).
    """
    final_bid = system.highest_bid
    if final_bid is None:
        return None

    final_bidder = next(
        (position for position, bid in system.history if bid == final_bid),
        None,
    )
    if final_bidder is None:
        return None

    for position, bid in system.history:
        if bid is None:
            continue
        if bid.denomination != final_bid.denomination:
            continue
        if position == final_bidder or position.partner == final_bidder:
            return position

    return final_bidder


def determine_contract(system: BiddingSystem) -> Contract | None:
    """Build the final Contract from a finished auction.

    Returns None if the auction was passed out (no bid was ever made),
    since there is no contract to play.
    """
    if system.highest_bid is None:
        return None

    declarer = determine_declarer(system)
    if declarer is None:
        return None

    return Contract(bid=system.highest_bid, declarer=declarer)
