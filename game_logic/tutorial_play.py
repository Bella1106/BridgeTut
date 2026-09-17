"""
tutorial_play.py
----------------
Converts prescribed Bid + Play tutorial play data into the
(Position, Card) format used by Lesson and LessonState.
"""

from card_model.card import Card, Rank, Suit
from card_model.deck import seating_order_from
from card_model.player import Position
from contract.contract import determine_contract
from game_logic.declarer import determine_opening_leader
from game_logic.guided_bidding import (
    GuidedBiddingLesson,
    GuidedBiddingState,
)
from game_logic.lesson import Lesson
from game_logic.tutorial_parser import TutorialLessonData

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


SUIT_MAP = {
    "S": Suit.SPADES,
    "H": Suit.HEARTS,
    "D": Suit.DIAMONDS,
    "C": Suit.CLUBS,
}


def parse_play_card(card_text: str) -> Card:
    """
    Parse Sonia's play notation such as AS, TH or 6D.
    """

    card_text = card_text.strip().upper()

    if len(card_text) != 2:
        raise ValueError(
            f"Invalid play card: {card_text}"
        )

    rank_text = card_text[0]
    suit_text = card_text[1]

    if rank_text not in RANK_MAP:
        raise ValueError(
            f"Invalid play card rank: {rank_text}"
        )

    if suit_text not in SUIT_MAP:
        raise ValueError(
            f"Invalid play card suit: {suit_text}"
        )

    return Card(
        RANK_MAP[rank_text],
        SUIT_MAP[suit_text],
    )


def parse_trick_line(
    line: str,
    leader: Position,
) -> list[tuple[Position, Card]]:
    """
    Parse one prescribed trick.

    The first card belongs to the trick leader.
    The remaining players follow clockwise.
    """

    card_texts = [
        card.strip()
        for card in line.split(",")
    ]

    if len(card_texts) != 4:
        raise ValueError(
            f"Trick must contain 4 cards, got {len(card_texts)}."
        )

    turn_order = seating_order_from(
        leader
    )

    return [
        (
            position,
            parse_play_card(card_text),
        )
        for position, card_text
        in zip(turn_order, card_texts)
    ]

def determine_trick_winner(
    trick: list[tuple[Position, Card]],
    trump_suit: Suit | None,
) -> Position:
    """
    Determine the winner of a completed four-card trick.

    A trump card beats any non-trump card.
    Otherwise, the highest card of the suit led wins.
    """

    if len(trick) != 4:
        raise ValueError(
            "A completed trick must contain exactly 4 cards."
        )

    led_suit = trick[0][1].suit

    # If at least one trump was played, only trump
    # cards are eligible to win.
    trump_cards = [
        (position, card)
        for position, card in trick
        if (
            trump_suit is not None
            and card.suit == trump_suit
        )
    ]

    if trump_cards:
        eligible_cards = trump_cards

    else:
        # With no trump played, only cards following
        # the suit led can win.
        eligible_cards = [
            (position, card)
            for position, card in trick
            if card.suit == led_suit
        ]

    winner, _ = max(
        eligible_cards,
        key=lambda played: played[1].rank,
    )

    return winner

def build_play_script(
    raw_play_lines: list[str],
    opening_leader: Position,
    trump_suit: Suit | None,
) -> list[tuple[Position, Card]]:
    """
    Convert all prescribed trick lines into the play script
    expected by Lesson and LessonState.

    The opening leader starts the first trick. The winner of
    each completed trick leads the next one.
    """

    script = []
    leader = opening_leader

    for line in raw_play_lines:
        trick = parse_trick_line(
            line,
            leader,
        )

        script.extend(trick)

        leader = determine_trick_winner(
            trick,
            trump_suit,
        )

    return script

def build_mode_one_lesson(
    data: TutorialLessonData,
) -> Lesson:
    """
    Convert parsed Bid + Play tutorial data into the guided
    play Lesson used by LessonState.

    The prescribed auction is replayed through the existing
    bidding system so the final contract, declarer and opening
    leader are derived using BridgeTut's normal game logic.
    """

    bidding_lesson = GuidedBiddingLesson(
        dealer=data.dealer,
        script=data.auction,
    )

    bidding_state = GuidedBiddingState(
        bidding_lesson
    )

    # Replay the authored auction exactly as prescribed.
    for position, call in data.auction:
        if not bidding_state.attempt_call(
            position,
            call,
        ):
            raise ValueError(
                "Tutorial contains an invalid bidding sequence."
            )

    contract = determine_contract(
        bidding_state.bidding_system
    )

    if contract is None:
        raise ValueError(
            "Bid + Play tutorial must produce a contract."
        )

    opening_leader = determine_opening_leader(
        contract.declarer
    )

    if opening_leader is None:
        raise ValueError(
            "Could not determine tutorial opening leader."
        )

    script = build_play_script(
        raw_play_lines=data.raw_play_lines,
        opening_leader=opening_leader,
        trump_suit=contract.trump_suit,
    )

    return Lesson(
        dealer=data.dealer,
        hands=data.hands,
        contract=contract,
        opening_leader=opening_leader,
        script=script,

        # During guided play Sonia wants the learner
        # to control South and North/dummy.
        user_seats=frozenset({
            Position.NORTH,
            Position.SOUTH,
        }),
    )