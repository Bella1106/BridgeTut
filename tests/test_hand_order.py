"""
Tests for the order a hand is displayed in.

Cards are shown left to right as: trump suit first, then suits
alternating black and red, with ranks descending inside each suit.
"""

from card_model.card import Card, Rank, Suit
from card_model.hand import Hand

def suits_in_order(hand, trump=None):
    "the suit of each card, left to right, with repeats collapsed"

    order = []

    for card in hand.sorted_by_suit(trump):

        if not order or order[-1] != card.suit:
            order.append(card.suit)

    return order

def one_card_per_suit():
    return Hand([
        Card(Rank.TWO, Suit.CLUBS),
        Card(Rank.TWO, Suit.DIAMONDS),
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.TWO, Suit.SPADES),
    ])

# =====================================================
# SUIT ORDER WITHOUT TRUMP
# =====================================================

def test_no_trump_orders_spades_hearts_clubs_diamonds():
    assert suits_in_order(one_card_per_suit()) == [
        Suit.SPADES,
        Suit.HEARTS,
        Suit.CLUBS,
        Suit.DIAMONDS,
    ]

# =====================================================
# SUIT ORDER WITH TRUMP
# =====================================================

def test_spade_trump_leads_with_spades():
    assert suits_in_order(one_card_per_suit(), Suit.SPADES) == [
        Suit.SPADES,
        Suit.HEARTS,
        Suit.CLUBS,
        Suit.DIAMONDS,
    ]

def test_heart_trump_leads_with_hearts():
    assert suits_in_order(one_card_per_suit(), Suit.HEARTS) == [
        Suit.HEARTS,
        Suit.CLUBS,
        Suit.DIAMONDS,
        Suit.SPADES,
    ]

def test_club_trump_leads_with_clubs():
    assert suits_in_order(one_card_per_suit(), Suit.CLUBS) == [
        Suit.CLUBS,
        Suit.DIAMONDS,
        Suit.SPADES,
        Suit.HEARTS,
    ]

def test_diamond_trump_leads_with_diamonds():
    assert suits_in_order(one_card_per_suit(), Suit.DIAMONDS) == [
        Suit.DIAMONDS,
        Suit.SPADES,
        Suit.HEARTS,
        Suit.CLUBS,
    ]

# =====================================================
# COLOUR ALTERNATION
# =====================================================

def test_colours_alternate_for_every_trump_suit():
    red = (Suit.HEARTS, Suit.DIAMONDS)

    for trump in (None, *Suit):

        order = suits_in_order(one_card_per_suit(), trump)

        colours = [suit in red for suit in order]

        assert colours == [
            colours[0],
            not colours[0],
            colours[0],
            not colours[0],
        ]

# =====================================================
# RANK ORDER
# =====================================================

def test_ranks_descend_within_a_suit():
    hand = Hand([
        Card(Rank.FOUR, Suit.HEARTS),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.TWO, Suit.HEARTS),
    ])

    assert [card.rank for card in hand.sorted_by_suit()] == [
        Rank.ACE,
        Rank.JACK,
        Rank.FOUR,
        Rank.TWO,
    ]

def test_trump_suit_ranks_also_descend():
    hand = Hand([
        Card(Rank.THREE, Suit.CLUBS),
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.ACE, Suit.SPADES),
    ])

    assert hand.sorted_by_suit(Suit.CLUBS) == [
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.THREE, Suit.CLUBS),
        Card(Rank.ACE, Suit.SPADES),
    ]

# =====================================================
# HAND CONTENTS UNCHANGED
# =====================================================

def test_sorting_keeps_every_card():
    hand = Hand([
        Card(Rank.TWO, Suit.CLUBS),
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.NINE, Suit.HEARTS),
    ])

    assert len(hand.sorted_by_suit(Suit.HEARTS)) == 3

    assert set(hand.sorted_by_suit(Suit.HEARTS)) == set(hand)

def test_void_suits_are_simply_absent():
    hand = Hand([
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.CLUBS),
    ])

    assert suits_in_order(hand, Suit.DIAMONDS) == [
        Suit.SPADES,
        Suit.CLUBS,
    ]
