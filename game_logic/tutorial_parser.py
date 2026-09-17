"""
Parses text-based Bid + Play tutorial lesson format.

This module converts tutorial lesson data into BridgeTut objects for:
- hands
- dealer
- vulnerability
- prescribed auction

The play script, Claim/Concede ending, and lesson note are retained
but are not yet converted into Alonso's LessonState objects.
"""

from dataclasses import dataclass

from bidding.bid import Bid
from bidding.bidding_system import SpecialCall
from card_model.card import Card, Rank, Suit
from card_model.player import Position
from game_logic.guided_bidding import (
    BiddingCall,
    parse_bidding_script,
)
from game_logic.vulnerability import Vulnerability


# =====================================================
# PARSED LESSON DATA
# =====================================================

@dataclass(frozen=True)
class TutorialLessonData:
    """Data extracted from one Bid + Play tutorial lesson."""

    hands: dict[Position, list[Card]]
    dealer: Position
    vulnerability: Vulnerability
    auction: list[tuple[Position, BiddingCall]]

    # Play data is retained but not yet converted into LessonState.
    raw_play_lines: list[str]
    ending: str | None
    note: str

# =====================================================
# CARD PARSING
# =====================================================

RANK_MAP = {
    "A": Rank.ACE,
    "K": Rank.KING,
    "Q": Rank.QUEEN,
    "J": Rank.JACK,
    "T": Rank.TEN,
    "9": Rank.NINE,
    "8": Rank.EIGHT,
    "7": Rank.SEVEN,
    "6": Rank.SIX,
    "5": Rank.FIVE,
    "4": Rank.FOUR,
    "3": Rank.THREE,
    "2": Rank.TWO,
}

SUIT_ORDER = [
    Suit.SPADES,
    Suit.HEARTS,
    Suit.DIAMONDS,
    Suit.CLUBS,
]

def parse_card(rank_text: str, suit: Suit) -> Card:
    """Convert Sonia's rank notation into a Card."""

    rank_text = rank_text.strip().upper()

    if rank_text not in RANK_MAP:
        raise ValueError(
            f"Invalid card rank: {rank_text}"
        )

    return Card(
        RANK_MAP[rank_text],
        suit,
    )

def parse_hand(hand_text: str) -> list[Card]:
    """Parse one hand in spades;hearts;diamonds;clubs order."""

    suit_groups = [
        group.strip()
        for group in hand_text.split(";")
    ]

    if len(suit_groups) != 4:
        raise ValueError(
            "Hand must contain spades, hearts, "
            "diamonds and clubs."
        )

    cards = []

    for suit, ranks in zip(SUIT_ORDER, suit_groups):

        # Sonia uses "-" for a void suit.
        # An empty group is also treated as a void.
        if ranks in {"-", ""}:
            continue

        for rank_text in ranks:
            cards.append(
                parse_card(rank_text, suit)
            )

    if len(cards) != 13:
        raise ValueError(
            f"Hand contains {len(cards)} cards, expected 13."
        )

    return cards

# =====================================================
# PLAYER / HAND PARSING
# =====================================================

POSITION_MAP = {
    "N": Position.NORTH,
    "S": Position.SOUTH,
    "E": Position.EAST,
    "W": Position.WEST,
}

def parse_hand_line(
    line: str,
) -> tuple[Position, list[Card]]:
    """Parse a line such as 'S: AKT74;76;5;AKQ43'."""

    if ":" not in line:
        raise ValueError(
            f"Invalid hand line: {line}"
        )

    position_text, hand_text = line.split(
        ":",
        maxsplit=1,
    )

    position_text = position_text.strip().upper()

    if position_text not in POSITION_MAP:
        raise ValueError(
            f"Invalid player position: {position_text}"
        )

    return (
        POSITION_MAP[position_text],
        parse_hand(hand_text.strip()),
    )

# =====================================================
# DEALER PARSING
# =====================================================

def parse_dealer(line: str) -> Position:
    """Parse a dealer line such as 'D: S'."""

    if not line.upper().startswith("D:"):
        raise ValueError(
            f"Invalid dealer line: {line}"
        )

    dealer_text = line.split(
        ":",
        maxsplit=1,
    )[1].strip().upper()

    if dealer_text not in POSITION_MAP:
        raise ValueError(
            f"Invalid dealer position: {dealer_text}"
        )

    return POSITION_MAP[dealer_text]

# =====================================================
# VULNERABILITY PARSING
# =====================================================

VULNERABILITY_MAP = {
    "NONE VUL": Vulnerability.NONE,
    "BOTH VUL": Vulnerability.BOTH,
    "NS VUL": Vulnerability.NORTH_SOUTH,
    "EW VUL": Vulnerability.EAST_WEST,
}

def parse_vulnerability(line: str) -> Vulnerability:
    """Parse Sonia's vulnerability notation."""

    vulnerability_text = line.strip().upper()

    if vulnerability_text not in VULNERABILITY_MAP:
        raise ValueError(
            f"Invalid vulnerability: {line}"
        )

    return VULNERABILITY_MAP[vulnerability_text]

# =====================================================
# COMPLETE BID + PLAY LESSON
# =====================================================

def parse_bid_and_play_lesson(
    lesson_text: str,
) -> TutorialLessonData:
    """Parse one complete Sonia Bid + Play lesson."""

    lines = [
        line.strip()
        for line in lesson_text.splitlines()
        if line.strip()
    ]

    if not lines:
        raise ValueError(
            "Lesson is empty."
        )

    # lessons begin with:
    # Cards held: spades;hearts;diamonds;clubs
    if not lines[0].lower().startswith(
        "cards held:"
    ):
        raise ValueError(
            "Lesson must begin with 'Cards held:'."
        )

    if len(lines) < 8:
        raise ValueError(
            "Lesson does not contain enough data."
        )

    # -------------------------------------------------
    # Hands
    # -------------------------------------------------

    hands = {}

    for line in lines[1:5]:
        position, hand = parse_hand_line(line)
        hands[position] = hand

    if set(hands) != set(Position):
        raise ValueError(
            "Lesson must contain all four hands."
        )

    # -------------------------------------------------
    # Dealer
    # -------------------------------------------------

    dealer = parse_dealer(
        lines[5]
    )

    # -------------------------------------------------
    # Vulnerability
    # -------------------------------------------------

    vulnerability = parse_vulnerability(
        lines[6]
    )

    # -------------------------------------------------
    # Prescribed auction
    # -------------------------------------------------

    auction = parse_bidding_script(
        lines[7],
        dealer,
    )

    # -------------------------------------------------
    # Play data
    # -------------------------------------------------
    #
    # We deliberately keep the actual plays as raw text
    # for now. Alonso's Lesson currently expects all
    # 52 cards to be played, whereas Sonia's lessons
    # may finish early with Claim or Concede.
    # -------------------------------------------------

    raw_play_lines = []
    ending = None
    note = ""

    for line in lines[8:]:

        if line.upper() in {
            "CLAIM",
            "CONCEDE",
        }:
            ending = line.capitalize()
            continue

        if line.upper().startswith(
            "NOTE:"
        ):
            note = line.split(
                ":",
                maxsplit=1,
            )[1].strip()
            continue

        raw_play_lines.append(line)

    return TutorialLessonData(
        hands=hands,
        dealer=dealer,
        vulnerability=vulnerability,
        auction=auction,
        raw_play_lines=raw_play_lines,
        ending=ending,
        note=note,
    )

# =====================================================
# MULTIPLE BID + PLAY LESSONS
# =====================================================

def parse_bid_and_play_lessons(
    file_text: str,
) -> list[TutorialLessonData]:
    """
    Parse a file containing multiple consecutive
    Bid + Play tutorial lessons.

    Each lesson begins with a 'Cards held:' header.
    """

    if not file_text.strip():
        raise ValueError(
            "Tutorial file is empty."
        )

    lesson_blocks = []
    current_block = []

    for line in file_text.splitlines():

        stripped_line = line.strip()

        if stripped_line.lower().startswith(
            "cards held:"
        ):
            # Starting a new lesson means the previous
            # lesson block is complete.
            if current_block:
                lesson_blocks.append(
                    "\n".join(current_block)
                )

            current_block = [
                stripped_line
            ]

        elif current_block:
            current_block.append(
                stripped_line
            )

    # Add the final lesson.
    if current_block:
        lesson_blocks.append(
            "\n".join(current_block)
        )

    if not lesson_blocks:
        raise ValueError(
            "No Bid + Play lessons found."
        )

    return [
        parse_bid_and_play_lesson(
            lesson_text
        )
        for lesson_text in lesson_blocks
    ]