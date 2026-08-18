"""
card.py
-------
Defines the fundamental building block of the game: a Card.

A standard Bridge deck has 52 cards, no jokers:
    4 suits: Clubs, Diamonds, Hearts, Spades
    13 ranks per suit: 2, 3, 4, 5, 6, 7, 8, 9, 10, Jack, Queen, King, Ace

This module also defines Suit and Rank as enums so the rest of the
codebase (bidding, contract, trick resolution) can compare cards safely
instead of relying on raw strings.
"""

from __future__ import annotations
from enum import IntEnum
from functools import total_ordering


class Suit(IntEnum):
    """Suits ordered the way they rank in Bridge bidding (low -> high).

    This ordering matters later for Bidding (1C < 1D < 1H < 1S < 1NT ...),
    so we define it once here and reuse it everywhere.
    """
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    @property
    def short(self) -> str:
        return {"CLUBS": "C", "DIAMONDS": "D", "HEARTS": "H", "SPADES": "S"}[self.name]

    @property
    def symbol(self) -> str:
        return {"CLUBS": "♣", "DIAMONDS": "♦",
                "HEARTS": "♥", "SPADES": "♠"}[self.name]

    def __str__(self) -> str:
        return self.short


class Rank(IntEnum):
    """Ranks ordered lowest -> highest, per the rules doc:
    2, 3, ..., 10, Jack, Queen, King, Ace.
    """
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @property
    def short(self) -> str:
        names = {11: "J", 12: "Q", 13: "K", 14: "A"}
        return names.get(self.value, str(self.value))

    def __str__(self) -> str:
        return self.short


@total_ordering
class Card:
    """A single playing card, e.g. Card(Rank.ACE, Suit.SPADES) -> 'AS'.

    __lt__/__eq__ give a total ordering (suit, then rank) purely so a hand
    can be sorted for display. That ordering does NOT decide who wins a
    trick -- for that, see beats() below, which depends on the suit led
    and the trump suit and belongs conceptually with trick_resolution.py.
    """

    __slots__ = ("rank", "suit")

    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other: "Card") -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        # Sort by suit first, then rank -- convenient for sorting a hand.
        return (self.suit, self.rank) < (other.suit, other.rank)

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))

    def __repr__(self) -> str:
        return f"{self.rank.short}{self.suit.short}"

    def beats(self, other: "Card", led_suit: Suit, trump: Suit | None) -> bool:
        """Return True if `self` beats `other` as the current best card
        of a trick, given the suit that was led and the trump suit
        (trump=None means a No Trump game).

        Rule (from the rules doc):
        - If it's a trump game and either card is a trump, the higher
          trump wins.
        - Otherwise the higher card of the suit led wins; a card that is
          not in the led suit and not trump cannot win.
        """
        self_is_trump = trump is not None and self.suit == trump
        other_is_trump = trump is not None and other.suit == trump

        if self_is_trump and not other_is_trump:
            return True
        if other_is_trump and not self_is_trump:
            return False
        if self_is_trump and other_is_trump:
            return self.rank > other.rank

        # Neither card is trump: only the suit led can win.
        self_follows = self.suit == led_suit
        other_follows = other.suit == led_suit
        if self_follows and not other_follows:
            return True
        if other_follows and not self_follows:
            return False
        if self_follows and other_follows:
            return self.rank > other.rank
        return False  # neither followed suit -- shouldn't normally happen
