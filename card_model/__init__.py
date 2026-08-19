"""
Card Model package for BridgeTut.

Owned by: Alonso (Sprint 1 backlog item "Card Model").
Everything else in the project (Bidding, Contract Logic, Trick
Resolution, Score Tracking) builds on the classes defined here:

    card.py   -> Suit, Rank, Card
    hand.py   -> Hand
    player.py -> Position, Player
    deck.py   -> Deck, new_deal()

Typical usage:

    from deck import new_deal
    from player import Position

    table = new_deal(dealer=Position.SOUTH)
    for pos, player in table.items():
        print(pos, player.hand)
"""
