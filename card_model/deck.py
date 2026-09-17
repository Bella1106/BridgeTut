"""
deck.py
-------
A standard 52-card deck (no jokers, matching the rules doc) plus dealing
logic for 4 players.
"""

from __future__ import annotations
import random
from typing import List

from .card import Card, Rank, Suit
from .player import Player, Position


class Deck:
    """A shuffleable, dealable deck of 52 cards."""

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)
        self.cards: List[Card] = self._fresh_52()

    @staticmethod
    def _fresh_52() -> List[Card]:
        return [Card(rank, suit) for suit in Suit for rank in Rank]

    def shuffle(self) -> None:
        self._rng.shuffle(self.cards)

    def deal(self, players: List[Player], cards_each: int = 13) -> None:
        """Deal `cards_each` cards to each player in turn, clockwise,
        starting from players[0]. Bridge deals all 52 cards (13 each to
        4 players) in one pass, one card at a time -- not 13 at once --
        which is what this loop does.

        Raises ValueError if there aren't enough cards left, so a bug
        (e.g. dealing twice from the same deck without reshuffling)
        fails loudly instead of silently dealing empty/short hands.
        """
        needed = cards_each * len(players)
        if needed > len(self.cards):
            raise ValueError(
                f"Cannot deal {cards_each} cards to {len(players)} players: "
                f"only {len(self.cards)} cards left in the deck."
            )
        for _ in range(cards_each):
            for player in players:
                player.hand.add(self.cards.pop())

    def __len__(self) -> int:
        return len(self.cards)


# --- helpers -----------------------------------------------------------

# Play/bidding always goes clockwise in this fixed order.
CLOCKWISE_ORDER = [Position.SOUTH, Position.WEST, Position.NORTH, Position.EAST]


def seating_order_from(dealer: Position) -> List[Position]:
    """Return the 4 positions in bidding/play order, starting at `dealer`
    and going clockwise (S -> W -> N -> E -> S), per the rules doc.
    """
    start = CLOCKWISE_ORDER.index(dealer)
    return CLOCKWISE_ORDER[start:] + CLOCKWISE_ORDER[:start]


def new_deal(dealer: Position, seed: int | None = None) -> dict[Position, Player]:
    """Convenience function: build 4 players seated N/S/E/W, shuffle a
    fresh deck, and deal 13 cards each starting with the dealer.

    Returns a dict keyed by Position so callers can look up e.g.
    players_by_position[Position.NORTH].
    """
    players = [Player(pos) for pos in seating_order_from(dealer)]
    deck = Deck(seed=seed)
    deck.shuffle()
    deck.deal(players)
    return {p.position: p for p in players}


def deal_from(hands: dict[Position, List[Card]]) -> dict[Position, Player]:
    """Build 4 players from exact, pre-specified hands rather than a
    shuffle -- for tutorial lessons, where the deal is fixed content
    rather than random.

    Raises ValueError if the hands don't form a legal deal: every
    position must be given exactly 13 cards, and the 4 hands together
    must cover all 52 cards with no duplicates or omissions.
    """
    missing = [pos for pos in Position if pos not in hands]
    if missing:
        raise ValueError(
            f"Missing hand(s) for: {[p.value for p in missing]}"
        )

    for position, cards in hands.items():
        if len(cards) != 13:
            raise ValueError(
                f"{position.value} has {len(cards)} cards, expected 13."
            )

    all_cards = [card for cards in hands.values() for card in cards]

    if len(set(all_cards)) != 52:
        raise ValueError(
            "Hands must cover all 52 cards exactly once "
            "(found a duplicate or a missing card)."
        )

    players = {position: Player(position) for position in Position}

    for position, cards in hands.items():
        for card in cards:
            players[position].hand.add(card)

    return players
