"""
test_card_model.py
-------------------
Basic tests for the Card Model, runnable with:

    python -m pytest test_card_model.py -v

or, without pytest installed:

    python test_card_model.py

These aren't exhaustive, but they lock in the behaviour the rest of the
team will depend on: 52 unique cards, 13 each, no overlap, correct
seating order, and correct trick-winning logic (both NT and trump games).
"""

import pytest

from card_model.card import Card, Rank, Suit
from card_model.deck import Deck, new_deal, seating_order_from
from card_model.hand import Hand
from card_model.player import Player, Position


def test_fresh_deck_has_52_unique_cards():
    deck = Deck(seed=1)
    assert len(deck) == 52
    assert len(set(deck.cards)) == 52


def test_deal_gives_13_cards_each_no_overlap():
    players = [Player(pos) for pos in
               (Position.SOUTH, Position.WEST, Position.NORTH, Position.EAST)]
    deck = Deck(seed=42)
    deck.shuffle()
    deck.deal(players)

    assert len(deck) == 0
    all_dealt = []
    for p in players:
        assert len(p.hand) == 13
        all_dealt.extend(list(p.hand))
    assert len(set(all_dealt)) == 52  # no duplicates, nothing missing


def test_dealing_too_many_cards_raises():
    players = [Player(pos) for pos in
               (Position.SOUTH, Position.WEST, Position.NORTH, Position.EAST)]
    deck = Deck(seed=1)
    deck.deal(players)  # uses up all 52
    try:
        deck.deal(players)
        assert False, "expected ValueError when deck is empty"
    except ValueError:
        pass


def test_seating_order_is_clockwise_from_dealer():
    assert seating_order_from(Position.SOUTH) == [
        Position.SOUTH, Position.WEST, Position.NORTH, Position.EAST]
    assert seating_order_from(Position.EAST) == [
        Position.EAST, Position.SOUTH, Position.WEST, Position.NORTH]


def test_partnerships():
    assert Position.NORTH.partner == Position.SOUTH
    assert Position.EAST.partner == Position.WEST
    assert Position.NORTH.is_north_south
    assert not Position.EAST.is_north_south


def test_card_ordering_for_sorting_a_hand():
    low = Card(Rank.TWO, Suit.CLUBS)
    high = Card(Rank.ACE, Suit.CLUBS)
    assert low < high


def test_beats_no_trump_highest_of_suit_led_wins():
    lead = Card(Rank.KING, Suit.HEARTS)
    follow = Card(Rank.ACE, Suit.HEARTS)
    off_suit = Card(Rank.ACE, Suit.SPADES)  # can't win, didn't follow suit
    assert follow.beats(lead, led_suit=Suit.HEARTS, trump=None)
    assert not off_suit.beats(lead, led_suit=Suit.HEARTS, trump=None)


def test_beats_trump_game_any_trump_beats_non_trump():
    lead = Card(Rank.ACE, Suit.HEARTS)     # highest possible of suit led
    small_trump = Card(Rank.TWO, Suit.SPADES)  # trumps are spades
    assert small_trump.beats(lead, led_suit=Suit.HEARTS, trump=Suit.SPADES)


def test_beats_trump_game_higher_trump_wins():
    small_trump = Card(Rank.TWO, Suit.SPADES)
    big_trump = Card(Rank.KING, Suit.SPADES)
    assert big_trump.beats(small_trump, led_suit=Suit.HEARTS, trump=Suit.SPADES)


def test_new_deal_convenience_function():
    table = new_deal(dealer=Position.NORTH, seed=7)
    assert set(table.keys()) == {Position.NORTH, Position.SOUTH,
                                  Position.EAST, Position.WEST}
    assert all(len(p.hand) == 13 for p in table.values())


def test_shuffle_is_deterministic_given_same_seed():
    "same seed must reproduce the same shuffle -- required for repeatable deals/replays"
    first = Deck(seed=99)
    first.shuffle()
    second = Deck(seed=99)
    second.shuffle()

    assert first.cards == second.cards


def test_deal_order_depends_on_dealer_not_just_seed():
    "same seed but a different dealer must still change who gets what"
    from_south = new_deal(dealer=Position.SOUTH, seed=5)
    from_north = new_deal(dealer=Position.NORTH, seed=5)

    assert (sorted(from_south[Position.SOUTH].hand)
            != sorted(from_north[Position.SOUTH].hand))


def test_hand_remove_missing_card_raises():
    "deliberate: playing a card you don't hold should fail loudly, not silently"
    hand = Hand([Card(Rank.TWO, Suit.CLUBS)])

    with pytest.raises(ValueError):
        hand.remove(Card(Rank.ACE, Suit.SPADES))


def test_hand_remove_removes_only_the_given_card():
    kept = Card(Rank.TWO, Suit.CLUBS)
    played = Card(Rank.ACE, Suit.SPADES)
    hand = Hand([kept, played])

    hand.remove(played)

    assert list(hand) == [kept]
    assert played not in hand


def test_hand_has_suit_reflects_current_contents():
    hand = Hand([Card(Rank.TWO, Suit.CLUBS)])

    assert hand.has_suit(Suit.CLUBS)
    assert not hand.has_suit(Suit.HEARTS)

    hand.remove(Card(Rank.TWO, Suit.CLUBS))

    assert not hand.has_suit(Suit.CLUBS)


def test_card_equality_against_non_card_is_false_not_an_error():
    card = Card(Rank.ACE, Suit.SPADES)

    assert card != "AS"
    assert card != 14


def test_card_repr_matches_short_notation():
    assert repr(Card(Rank.ACE, Suit.SPADES)) == "AS"
    assert repr(Card(Rank.TEN, Suit.CLUBS)) == "10C"


def test_position_str_is_single_letter():
    assert str(Position.NORTH) == "N"
    assert str(Position.SOUTH) == "S"


if __name__ == "__main__":
    # Allow running without pytest: just call every test_* function.
    import sys
    tests = [(n, f) for n, f in list(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {name}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
