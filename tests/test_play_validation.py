from card_model.card import Card, Suit, Rank
from card_model.hand import Hand
from game_logic.play_validation import is_valid_play

def test_first_player_can_play_any_card():
    hand = Hand([
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS),
    ])

    card = Card(Rank.KING, Suit.CLUBS)

    assert is_valid_play(hand, card, None)


def test_player_can_follow_led_suit():
    hand = Hand([
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS),
    ])

    card = Card(Rank.ACE, Suit.HEARTS)

    assert is_valid_play(hand, card, Suit.HEARTS)


def test_player_cannot_play_other_suit_when_able_to_follow():
    hand = Hand([
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS),
    ])

    card = Card(Rank.KING, Suit.CLUBS)

    assert not is_valid_play(hand, card, Suit.HEARTS)


def test_player_can_play_other_suit_when_unable_to_follow():
    hand = Hand([
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.ACE, Suit.SPADES),
    ])

    card = Card(Rank.KING, Suit.CLUBS)

    assert is_valid_play(hand, card, Suit.HEARTS)

def test_card_not_in_hand_is_rejected():
    hand = Hand([
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.CLUBS),
    ])

    card = Card(Rank.QUEEN, Suit.HEARTS)

    assert not is_valid_play(hand, card, Suit.HEARTS)


def test_player_can_play_trump_when_unable_to_follow():
    hand = Hand([
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.CLUBS),
    ])

    card = Card(Rank.ACE, Suit.SPADES)

    # Hearts were led, but the player has no Hearts
    assert is_valid_play(hand, card, Suit.HEARTS)


def test_player_is_not_forced_to_play_trump_when_unable_to_follow():
    hand = Hand([
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.CLUBS),
    ])

    card = Card(Rank.KING, Suit.CLUBS)

    # Even if Spades were trump, a player who cannot follow Hearts
    # may discard another suit instead
    assert is_valid_play(hand, card, Suit.HEARTS)


def test_validation_does_not_remove_card_from_hand():
    card = Card(Rank.ACE, Suit.HEARTS)

    hand = Hand([
        card,
        Card(Rank.KING, Suit.CLUBS),
    ])

    assert is_valid_play(hand, card, Suit.HEARTS)

    assert card in hand


def test_player_with_one_card_can_play_when_following_suit():
    card = Card(Rank.ACE, Suit.HEARTS)
    hand = Hand([card])

    assert is_valid_play(hand, card, Suit.HEARTS)