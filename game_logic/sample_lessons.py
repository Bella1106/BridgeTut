"""
sample_lessons.py
------------------
PLACEHOLDER CONTENT.

One hardcoded Lesson, purely so Mode 2's route/auto-play/hidden-hand
wiring has something real to load. It is not a properly authored
lesson -- the deal and the "correct" line are arbitrary, not chosen
to teach anything. Replace with real authored lessons.
"""

from bidding.bid import Bid, Denomination

from card_model.deck import Deck, seating_order_from
from card_model.player import Position

from contract.contract import Contract

from .declarer import determine_opening_leader
from .lesson import Lesson


def build_sample_lesson() -> Lesson:

    cards = Deck(seed=101).cards

    positions = [
        Position.NORTH,
        Position.EAST,
        Position.SOUTH,
        Position.WEST,
    ]

    hands = {
        position: cards[i * 13:(i + 1) * 13]
        for i, position in enumerate(positions)
    }

    declarer = Position.SOUTH

    contract = Contract(
        bid=Bid(1, Denomination.NO_TRUMP),
        declarer=declarer,
    )

    opening_leader = determine_opening_leader(declarer)

    #script the first trick only -- enough to exercise a user play,
    #a computer auto-play, and a hidden hand, in one small lesson
    trick_order = seating_order_from(opening_leader)

    script = [
        (position, hands[position][0])
        for position in trick_order
    ]

    return Lesson(
        dealer=Position.SOUTH,
        hands=hands,
        contract=contract,
        opening_leader=opening_leader,
        script=script,
        user_seats=frozenset({Position.NORTH, Position.SOUTH}),
    )
