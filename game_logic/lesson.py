"""
lesson.py
---------
Runs a tutorial lesson: a fixed deal, a fixed contract (no auction),
and one exact, pre-scripted line of play.

A Lesson is authored content -- the hands, the contract, and the
correct card-by-card sequence. LessonState walks through that script
as cards are played and checks each one against it.

This module deliberately knows nothing about *why* a card is correct
(no trick-winning, no play validation) -- the script already encodes a
legal line, so LessonState only ever needs to compare against it.

Lessons are not saved to game history. They are practice, not games.
"""

from dataclasses import dataclass, field

from card_model.card import Card
from card_model.player import Position
from contract.contract import Contract

@dataclass(frozen=True)
class Lesson:

    dealer: Position
    hands: dict[Position, list[Card]]
    contract: Contract
    opening_leader: Position

    #the exact expected line of play, one (player, card) per play
    script: list[tuple[Position, Card]]

    #seats the learner plays themselves; the rest are scripted
    user_seats: frozenset[Position]

    def __post_init__(self):

        missing = [
            position for position in Position
            if position not in self.hands
        ]

        if missing:
            raise ValueError(
                f"Lesson is missing hand(s) for: "
                f"{[p.value for p in missing]}"
            )

        if len(self.script) != 52:
            raise ValueError(
                f"Lesson script has {len(self.script)} plays, expected 52."
            )

        for position in Position:

            hand = set(self.hands[position])

            if len(hand) != 13:
                raise ValueError(
                    f"{position.value}'s hand has "
                    f"{len(hand)} unique cards, expected 13."
                )

            scripted = {
                card for played_by, card in self.script
                if played_by == position
            }

            if scripted != hand:
                raise ValueError(
                    f"Lesson script does not play exactly "
                    f"{position.value}'s hand."
                )

@dataclass
class Mistake:

    #index into the script at which the wrong card was tried
    step: int

    position: Position
    expected_card: Card
    attempted_card: Card

class LessonState:
    """Tracks progress through a Lesson's script as cards are played."""

    def __init__(self, lesson: Lesson):

        self.lesson = lesson

        self.plays_made: list[tuple[Position, Card]] = []

        self.mistakes: list[Mistake] = []

    @property
    def step(self) -> int:

        "how many correct plays have been made so far"

        return len(self.plays_made)

    @property
    def current_player(self) -> Position | None:

        "whose turn it is, or None once the lesson is complete"

        if self.is_complete():
            return None

        return self.lesson.script[self.step][0]

    @property
    def expected_card(self) -> Card | None:

        "the next card the script calls for, or None once complete"

        if self.is_complete():
            return None

        return self.lesson.script[self.step][1]

    def is_user_turn(self) -> bool:

        "whether the learner (rather than the script) controls this play"

        return self.current_player in self.lesson.user_seats

    def is_complete(self) -> bool:

        return self.step >= len(self.lesson.script)

    def attempt_play(self, position: Position, card: Card) -> bool:
        """Try to play `card` as `position`.

        Records and advances on a match. On a mismatch, records a
        Mistake and leaves the state where it was, so the learner can
        simply try again.
        """

        if self.is_complete():
            return False

        if (
            position == self.current_player
            and card == self.expected_card
        ):
            self.plays_made.append((position, card))

            return True

        self.mistakes.append(
            Mistake(
                step=self.step,
                position=self.current_player,
                expected_card=self.expected_card,
                attempted_card=card,
            )
        )

        return False

    @property
    def mistake_count(self) -> int:

        return len(self.mistakes)
