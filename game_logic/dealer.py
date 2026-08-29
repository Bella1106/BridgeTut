"""
Determines dealer rotation between bridge deals.

The dealer rotates clockwise after each deal. 
"""

from card_model.player import Position
from card_model.deck import seating_order_from

def determine_next_dealer(
        current_dealer: Position
) -> Position:

    dealer_order = seating_order_from(current_dealer)

    return dealer_order[1]