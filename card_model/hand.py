"""
hand.py
-------
A Hand is the set of cards a player is currently holding.

Kept separate from Player so other modules (e.g. play_validation.py,
contract_logic.py) can reason about "a hand" on its own -- for example
when displaying a hand, or checking whether a hand can follow a suit --
without needing a full Player object.
"""

from __future__ import annotations
from typing import Iterable, List

from .card import Card, Suit


class Hand:
    """The cards currently held by one player (starts empty, filled by
    Deck.deal, and shrinks as cards are played during the Playing phase).
    """

    def __init__(self, cards: Iterable[Card] | None = None):
        self._cards: List[Card] = list(cards) if cards else []

    def add(self, card: Card) -> None:
        self._cards.append(card)

    def remove(self, card: Card) -> None:
        """Play/discard a card from the hand.

        Raises ValueError (via list.remove) if the card isn't actually
        in the hand -- that's deliberate: silently ignoring an attempt
        to play a card you don't hold would hide a bug in the caller.
        """
        self._cards.remove(card)

    def has_suit(self, suit: Suit) -> bool:
        """Used by play validation: must a player follow suit, or are
        they free to play anything because they're void in that suit?
        """
        return any(card.suit == suit for card in self._cards)

    def cards_of(self, suit: Suit) -> List[Card]:
        return [c for c in self._cards if c.suit == suit]

    def sorted_by_suit(self) -> List[Card]:
        return sorted(self._cards)

    def __contains__(self, card: Card) -> bool:
        return card in self._cards

    def __iter__(self):
        return iter(self._cards)

    def __len__(self) -> int:
        return len(self._cards)

    def __repr__(self) -> str:
        by_suit = {s: self.cards_of(s) for s in Suit}
        parts = []
        for suit in reversed(list(Suit)):  # Spades, Hearts, Diamonds, Clubs
            ranks = "".join(c.rank.short for c in sorted(
                by_suit[suit], key=lambda c: c.rank, reverse=True))
            parts.append(f"{suit.symbol} {ranks or '-'}")
        return "  ".join(parts)
