from bidding.bid import Bid, Denomination
from card_model.card import Card, Rank, Suit
from card_model.player import Position
from game_logic.tutorial_parser import (
    parse_card,
    parse_hand,
    parse_hand_line,
    parse_dealer,
    parse_vulnerability,
    parse_bid_and_play_lesson,
)
from game_logic.vulnerability import Vulnerability


# =====================================================
# CARD PARSING
# =====================================================

def test_parse_card():
    card = parse_card(
        "A",
        Suit.SPADES,
    )

    assert card == Card(
        Rank.ACE,
        Suit.SPADES,
    )


def test_parse_ten_uses_t_notation():
    card = parse_card(
        "T",
        Suit.HEARTS,
    )

    assert card == Card(
        Rank.TEN,
        Suit.HEARTS,
    )


def test_invalid_card_rank_is_rejected():
    try:
        parse_card(
            "X",
            Suit.SPADES,
        )

        assert False

    except ValueError:
        assert True


# =====================================================
# HAND PARSING
# =====================================================

def test_parse_south_hand():
    hand = parse_hand(
        "K3;K83;A72;AQ865"
    )

    assert len(hand) == 13

    assert Card(
        Rank.KING,
        Suit.SPADES,
    ) in hand

    assert Card(
        Rank.THREE,
        Suit.SPADES,
    ) in hand

    assert Card(
        Rank.ACE,
        Suit.DIAMONDS,
    ) in hand

    assert Card(
        Rank.FIVE,
        Suit.CLUBS,
    ) in hand


def test_parse_void_suit():
    hand = parse_hand(
        "542;-;K532;KT9532"
    )

    assert len(hand) == 13

    hearts = [
        card
        for card in hand
        if card.suit == Suit.HEARTS
    ]

    assert hearts == []


def test_hand_with_wrong_number_of_cards_is_rejected():
    try:
        parse_hand(
            "AKQ;AKQ;AKQ;AKQ"
        )

        assert False

    except ValueError:
        assert True


# =====================================================
# HAND LINE PARSING
# =====================================================

def test_parse_hand_line():
    position, hand = parse_hand_line(
        "S: K3;K83;A72;AQ865"
    )

    assert position == Position.SOUTH
    assert len(hand) == 13


# =====================================================
# DEALER PARSING
# =====================================================

def test_parse_dealer():
    dealer = parse_dealer(
        "D: S"
    )

    assert dealer == Position.SOUTH


# =====================================================
# VULNERABILITY PARSING
# =====================================================

def test_parse_both_vulnerable():
    vulnerability = parse_vulnerability(
        "BOTH VUL"
    )

    assert vulnerability == Vulnerability.BOTH


def test_parse_none_vulnerable():
    vulnerability = parse_vulnerability(
        "NONE VUL"
    )

    assert vulnerability == Vulnerability.NONE


# =====================================================
# COMPLETE SONIA BID + PLAY LESSON
# =====================================================

def test_parse_complete_sonia_lesson():
    lesson_text = """
Cards held: spades;hearts;diamonds;clubs
N: AQJT;AQ53;KJ6;42
S: K3;K83;A72;AQ865
E: 942;T2;T943;KJT9
W: 8765;J974;Q85;73
D: S
BOTH VUL
1NT;P;2C;P;2D;P;6NT.
8S,TS,9S,3S
4C,9C,QC,3C
8C,7C,2C,TC
4S,KS,7S,JS
KH,4H,3H,TH
8H,9H,AH,2H
QH,2S,6H,7H
6D,3D,AD,5D
2D,8D,JD,4D
Claim
NOTE: when testing a suit break in NT, try keep the controlling card in case it doesn't: concede an early trick (when you can afford it) instead of later when you can't afford it.
"""

    lesson = parse_bid_and_play_lesson(
        lesson_text
    )

    # ---------------------------------------------
    # Dealer and vulnerability
    # ---------------------------------------------

    assert lesson.dealer == Position.SOUTH

    assert (
        lesson.vulnerability
        == Vulnerability.BOTH
    )

    # ---------------------------------------------
    # Hands
    # ---------------------------------------------

    assert len(lesson.hands) == 4

    assert all(
        len(hand) == 13
        for hand in lesson.hands.values()
    )

    assert Card(
        Rank.ACE,
        Suit.SPADES,
    ) in lesson.hands[Position.NORTH]

    assert Card(
        Rank.KING,
        Suit.SPADES,
    ) in lesson.hands[Position.SOUTH]

    # ---------------------------------------------
    # Auction
    # ---------------------------------------------

    assert len(lesson.auction) == 7

    assert lesson.auction[0] == (
        Position.SOUTH,
        Bid(
            1,
            Denomination.NO_TRUMP,
        ),
    )

    assert lesson.auction[1] == (
        Position.WEST,
        None,
    )

    assert lesson.auction[-1] == (
        Position.NORTH,
        Bid(
            6,
            Denomination.NO_TRUMP,
        ),
    )

    # ---------------------------------------------
    # Play data
    # ---------------------------------------------

    assert len(
        lesson.raw_play_lines
    ) == 9

    assert lesson.raw_play_lines[0] == (
        "8S,TS,9S,3S"
    )

    assert lesson.raw_play_lines[-1] == (
        "2D,8D,JD,4D"
    )

    # ---------------------------------------------
    # Lesson ending
    # ---------------------------------------------

    assert lesson.ending == "Claim"

    # ---------------------------------------------
    # Teaching note
    # ---------------------------------------------

    assert lesson.note.startswith(
        "when testing a suit break in NT"
    )

    assert "controlling card" in lesson.note