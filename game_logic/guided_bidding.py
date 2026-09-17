"""
guided_bidding.py
-----------------
Runs the guided bidding phase of a Bid + Play tutorial lesson.

The auction follows one exact, pre-scripted sequence of calls.
The learner controls South. Calls for the other three players are
scripted by the lesson.

A wrong learner call is rejected and recorded as a mistake without
advancing the auction.
"""

from dataclasses import dataclass

from bidding.bid import Bid
from bidding.bidding_system import BiddingSystem, SpecialCall
from card_model.player import Position


# None represents Pass, consistent with BiddingSystem.
BiddingCall = Bid | SpecialCall | None


@dataclass(frozen=True)
class GuidedBiddingLesson:
    """The authored bidding content for a Bid + Play lesson."""

    dealer: Position
    script: list[tuple[Position, BiddingCall]]
    user_seat: Position = Position.SOUTH

    def __post_init__(self):
        if not self.script:
            raise ValueError(
                "Guided bidding script cannot be empty."
            )

        if self.script[0][0] != self.dealer:
            raise ValueError(
                "First scripted call must be made by the dealer."
            )


@dataclass
class BiddingMistake:
    """Records an incorrect call made by the learner."""

    step: int
    position: Position
    expected_call: BiddingCall
    attempted_call: BiddingCall


class GuidedBiddingState:
    """Tracks progress through a prescribed bidding sequence."""

    def __init__(self, lesson: GuidedBiddingLesson):
        self.lesson = lesson
        self.bidding_system = BiddingSystem(lesson.dealer)

        self.calls_made: list[
            tuple[Position, BiddingCall]
        ] = []

        self.mistakes: list[BiddingMistake] = []

    @property
    def step(self) -> int:
        return len(self.calls_made)

    @property
    def current_player(self) -> Position | None:
        if self.is_complete():
            return None

        return self.lesson.script[self.step][0]

    @property
    def expected_call(self) -> BiddingCall:
        if self.is_complete():
            return None

        return self.lesson.script[self.step][1]

    def is_user_turn(self) -> bool:
        return (
            not self.is_complete()
            and self.current_player == self.lesson.user_seat
        )

    def is_complete(self) -> bool:
        return self.step >= len(self.lesson.script)

    def _apply_call(
        self,
        position: Position,
        call: BiddingCall,
    ) -> bool:
        """Apply a scripted call through the existing bidding system."""

        if call is None:
            return self.bidding_system.make_pass(position)

        if call == SpecialCall.DOUBLE:
            return self.bidding_system.make_double(position)

        if call == SpecialCall.REDOUBLE:
            return self.bidding_system.make_redouble(position)

        return self.bidding_system.make_bid(position, call)

    def attempt_call(
        self,
        position: Position,
        call: BiddingCall,
    ) -> bool:
        """Attempt the learner's next call.

        The call must match the prescribed lesson script.
        An incorrect call is recorded without advancing the lesson.
        """

        if self.is_complete():
            return False

        if (
            position != self.current_player
            or call != self.expected_call
        ):
            self.mistakes.append(
                BiddingMistake(
                    step=self.step,
                    position=position,
                    expected_call=self.expected_call,
                    attempted_call=call,
                )
            )
            return False

        if not self._apply_call(position, call):
            return False

        self.calls_made.append((position, call))

        return True

    def play_computer_calls(self) -> None:
        """Advance scripted computer calls until South must act."""

        while (
            not self.is_complete()
            and not self.is_user_turn()
        ):
            position = self.current_player
            call = self.expected_call

            if not self._apply_call(position, call):
                raise ValueError(
                    "Script contains an invalid bidding sequence."
                )

            self.calls_made.append((position, call))

    @property
    def mistake_count(self) -> int:
        return len(self.mistakes)