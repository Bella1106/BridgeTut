from pathlib import Path
import pytest

from bidding.bid import Bid, Denomination
from bidding.bidding_system import SpecialCall
from card_model.card import Card, Rank, Suit
from card_model.player import Position
from game_logic.tutorial_parser import (
    parse_card,
    parse_hand,
    parse_hand_line,
    parse_dealer,
    parse_vulnerability,
    parse_bid_and_play_lesson,
    parse_bid_and_play_lessons,
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
        "S: K3;K86;A72;AQ865"
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
S: K3;K86;A72;AQ865
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

# =====================================================
# MULTIPLE BID + PLAY LESSONS
# =====================================================

def test_parse_multiple_lessons():
    file_text = """
Cards held: spades;hearts;diamonds;clubs
N: AQJT;AQ53;KJ6;42
S: K3;K86;A72;AQ865
E: 942;T2;T943;KJT9
W: 8765;J974;Q85;73
D: S
BOTH VUL
1NT;P;2C;P;2D;P;6NT.
8S,TS,9S,3S
Claim
NOTE: First lesson.

Cards held: spades;hearts;diamonds;clubs
N: J64;T543;A73;Q64
S: AQ8753;AQ;K65;A7
E: KT9;K98;JT42;K82
W: 2;J762;Q98;JT953
D: N
NONE VUL
P;P;1S;P;1NT;P;3S;P;4S.
JC,QC,KC,AC
Claim
NOTE: Second lesson.
"""

    lessons = parse_bid_and_play_lessons(
        file_text
    )

    assert len(lessons) == 2

    assert (
        lessons[0].dealer
        == Position.SOUTH
    )

    assert (
        lessons[0].vulnerability
        == Vulnerability.BOTH
    )

    assert (
        lessons[1].dealer
        == Position.NORTH
    )

    assert (
        lessons[1].vulnerability
        == Vulnerability.NONE
    )

    assert lessons[0].ending == "Claim"
    assert lessons[1].ending == "Claim"

    assert lessons[0].note == (
        "First lesson."
    )

    assert lessons[1].note == (
        "Second lesson."
    )


def test_empty_tutorial_file_is_rejected():
    try:
        parse_bid_and_play_lessons(
            ""
        )

        assert False

    except ValueError:
        assert True


def test_text_without_lessons_is_rejected():
    try:
        parse_bid_and_play_lessons(
            "This file contains no lessons."
        )

        assert False

    except ValueError:
        assert True

# =====================================================
# REAL SPONSOR BID + PLAY FILE
# =====================================================

def test_parse_real_sponsor_bid_and_play_file():
    fixture_path = (
        Path(__file__).parent
        / "lessons"
        / "exampleBidAndPlay.txt"
    )

    file_text = fixture_path.read_text(
        encoding="utf-8"
    )

    lessons = parse_bid_and_play_lessons(
        file_text
    )

    assert len(lessons) == 3

    # ---------------------------------------------
    # Lesson 1
    # ---------------------------------------------

    first = lessons[0]

    assert first.dealer == Position.SOUTH
    assert first.vulnerability == Vulnerability.BOTH
    assert len(first.auction) == 7
    assert len(first.raw_play_lines) == 9
    assert first.ending == "Claim"

    assert first.auction[-1] == (
        Position.NORTH,
        Bid(
            6,
            Denomination.NO_TRUMP,
        ),
    )

    # ---------------------------------------------
    # Lesson 2
    # ---------------------------------------------

    second = lessons[1]

    assert second.dealer == Position.SOUTH
    assert second.vulnerability == Vulnerability.BOTH
    assert len(second.auction) == 16
    assert len(second.raw_play_lines) == 8
    assert second.ending == "Claim"

    # Sonia's real auction contains:
    # 2C;3H;DBL;P;...
    assert second.auction[2] == (
        Position.NORTH,
        SpecialCall.DOUBLE,
    )

    assert second.auction[-1] == (
        Position.EAST,
        Bid(
            6,
            Denomination.SPADES,
        ),
    )

    # ---------------------------------------------
    # Lesson 3
    # ---------------------------------------------

    third = lessons[2]

    assert third.dealer == Position.NORTH
    assert third.vulnerability == Vulnerability.NONE
    assert len(third.auction) == 9
    assert len(third.raw_play_lines) == 8
    assert third.ending == "Claim"

    assert third.auction[-1] == (
        Position.NORTH,
        Bid(
            4,
            Denomination.SPADES,
        ),
    )

    # Every real lesson should contain its
    # teaching note.
    assert all(
        lesson.note
        for lesson in lessons
    )

#test deliberatly contains incorrect data
def test_duplicate_and_missing_card_in_deal_is_rejected():
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
Claim
NOTE: Test lesson.
"""

    with pytest.raises(
        ValueError,
        match="Invalid tutorial deal",
    ):
        parse_bid_and_play_lesson(
            lesson_text
        )