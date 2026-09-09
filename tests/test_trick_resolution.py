from card_model.card import Card, Rank, Suit
from card_model.player import Position

from game_logic.trick_resolution import (determine_led_suit, determine_trick_winner)

# =====================================================
# LED SUIT TESTS
# =====================================================

def test_led_suit_is_first_card_played():
    plays = {
        Position.SOUTH: Card(Rank.TWO, Suit.HEARTS),
        Position.WEST: Card(Rank.KING, Suit.CLUBS),
    }

    assert determine_led_suit(plays) == Suit.HEARTS

def test_led_suit_of_empty_trick_is_none():
    assert determine_led_suit({}) is None

# =====================================================
# NO TRUMP TESTS
# =====================================================

def test_highest_card_of_led_suit_wins_no_trump():
    plays = {
        Position.SOUTH: Card(Rank.TWO, Suit.HEARTS),
        Position.WEST: Card(Rank.KING, Suit.HEARTS),
        Position.NORTH: Card(Rank.ACE, Suit.HEARTS),
        Position.EAST: Card(Rank.QUEEN, Suit.HEARTS),
    }

    assert determine_trick_winner(plays, trump=None) == Position.NORTH

def test_card_not_in_led_suit_cannot_win_no_trump():
    plays = {
        Position.SOUTH: Card(Rank.TWO, Suit.HEARTS),
        Position.WEST: Card(Rank.ACE, Suit.CLUBS),
        Position.NORTH: Card(Rank.THREE, Suit.HEARTS),
        Position.EAST: Card(Rank.FOUR, Suit.HEARTS),
    }

    assert determine_trick_winner(plays, trump=None) == Position.EAST

# =====================================================
# TRUMP TESTS
# =====================================================

def test_lowest_trump_beats_highest_led_suit_card():
    plays = {
        Position.SOUTH: Card(Rank.ACE, Suit.HEARTS),
        Position.WEST: Card(Rank.TWO, Suit.SPADES),
        Position.NORTH: Card(Rank.KING, Suit.HEARTS),
        Position.EAST: Card(Rank.QUEEN, Suit.HEARTS),
    }

    assert determine_trick_winner(plays, trump=Suit.SPADES) == Position.WEST

def test_highest_trump_wins_when_multiple_trumps_played():
    plays = {
        Position.SOUTH: Card(Rank.TWO, Suit.SPADES),
        Position.WEST: Card(Rank.ACE, Suit.HEARTS),
        Position.NORTH: Card(Rank.KING, Suit.SPADES),
        Position.EAST: Card(Rank.FOUR, Suit.CLUBS),
    }

    assert determine_trick_winner(plays, trump=Suit.SPADES) == Position.NORTH

def test_leader_wins_when_no_one_follows_or_trumps():
    plays = {
        Position.SOUTH: Card(Rank.TWO, Suit.HEARTS),
        Position.WEST: Card(Rank.ACE, Suit.CLUBS),
        Position.NORTH: Card(Rank.KING, Suit.DIAMONDS),
        Position.EAST: Card(Rank.QUEEN, Suit.DIAMONDS),
    }

    assert determine_trick_winner(plays, trump=Suit.SPADES) == Position.SOUTH

# =====================================================
# EMPTY TRICK
# =====================================================

def test_empty_trick_has_no_winner():
    assert determine_trick_winner({}, trump=None) is None
