"""
trick_resolution.py
--------------------
Determines the winner of a completed trick.

A trick is one card from each of the four players, played in turn
starting with the leader. The winner is whoever played the highest
card of the suit led, unless a trump was played, in which case the
highest trump wins (see Card.beats() in card_model/card.py, which
already encodes those comparison rules).

Plays are represented as a dict mapping Position -> Card, in the
order the cards were played (the leader's card is inserted first).
This matches how tricks are already built up in the Play page.
"""

from card_model.card import Card, Suit
from card_model.player import Position


def determine_led_suit(
        plays: dict[Position, Card],
) -> Suit | None:

    "the suit of the first card played this trick, or None if empty"

    if not plays:
        return None

    first_card = next(iter(plays.values()))

    return first_card.suit


def determine_trick_winner(
        plays: dict[Position, Card],
        trump: Suit | None,
) -> Position | None:

    "the position whose card wins the trick, or None if empty"

    if not plays:
        return None

    led_suit = determine_led_suit(plays)

    winning_position = None
    winning_card = None

    for position, card in plays.items():

        if winning_card is None or card.beats(winning_card, led_suit, trump):
            winning_position = position
            winning_card = card

    return winning_position
