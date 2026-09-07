"""
Validates card plays during the play phase of Contract Bridge

A player must follow the suit that was led if they are able to
If they do not hold a card of the led suit, play any card
The first player of a trick may lead any card from their hand
"""

from card_model.card import Card, Suit
from card_model.hand import Hand

def is_valid_play(
        hand: Hand,
        card: Card,
        led_suit: Suit | None,
) -> bool:

    #player cannot play card not held
    if card not in hand:
        return False

    #opening card of trick may be any card
    if led_suit is None:
        return True

    #print("led suit:", led_suit)
    #print("card suit:", card.suit)
    #print("hand has led suit:", hand.has_suit(led_suit))

    #if player can follow suit, they must follow
    if hand.has_suit(led_suit):
        return card.suit == led_suit

    #if player cannot follow suit, play any card
    return True