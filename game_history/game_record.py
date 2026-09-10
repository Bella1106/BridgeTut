"""
Stores the history of a single BridgeTut game.

A GameRecord contains:

- Game information
- Bidding information
- Notes
- All played tricks
- Trick winners
- Scoring information
"""

from datetime import datetime


class GameRecord:

    def __init__(
        self,
        game_id,
        dealer,
        players,
        contract=None,
        declarer=None,
        bidding_history=None,
        notes="",
        vulnerable=False,
        doubled=False,
    ):

        # =================================================
        # GAME INFORMATION
        # =================================================

        self.game_id = game_id

        self.created_at = datetime.now()

        self.dealer = dealer

        self.players = players

        self.contract = contract

        self.declarer = declarer

        self.bidding_history = (
            bidding_history
            if bidding_history is not None
            else []
        )

        self.notes = notes

        self.vulnerable = vulnerable

        self.doubled = doubled

        # =================================================
        # PLAY HISTORY
        # =================================================

        # Each item represents one completed trick.
        #
        # Example:
        #
        # {
        #     "trick_number": 1,
        #     "plays": {
        #         Position.NORTH: card,
        #         Position.EAST: card,
        #         Position.SOUTH: card,
        #         Position.WEST: card,
        #     },
        #     "winner": Position.NORTH
        # }

        self.tricks = []

        # =================================================
        # SCORING
        # =================================================

        self.final_score = None

        self.result = None

    # =====================================================
    # NOTES
    # =====================================================

    def set_notes(self, notes):

        self.notes = notes

    # =====================================================
    # PLAY DATA
    # =====================================================

    def add_trick(
        self,
        trick_number,
        plays,
        winner=None,
    ):
        """
        Store one completed trick.

        Parameters
        ----------
        trick_number : int
            Number of the trick, from 1 to 13.

        plays : dict
            Dictionary mapping Position -> Card.

        winner : Position | None
            Player who won the trick.
        """

        trick = {
            "trick_number": trick_number,
            "plays": dict(plays),
            "winner": winner,
        }

        self.tricks.append(
            trick
        )

    # =====================================================
    # PLAY INFORMATION
    # =====================================================

    @property
    def tricks_played(self):

        return len(
            self.tricks
        )

    @property
    def is_complete(self):

        return (
            self.tricks_played >= 13
        )

    # =====================================================
    # CONTRACT INFORMATION
    # =====================================================

    @property
    def tricks_required(self):

        if self.contract is None:

            return None

        return (
            self.contract.level
            + 6
        )

    # =====================================================
    # TRICK COUNT
    # =====================================================

    @property
    def declarer_tricks(self):

        if self.declarer is None:

            return 0

        partner = self.declarer.partner

        return sum(
            1
            for trick in self.tricks
            if trick.get("winner")
            in (
                self.declarer,
                partner,
            )
        )

    @property
    def defence_tricks(self):

        return (
            self.tricks_played
            - self.declarer_tricks
        )

    # =====================================================
    # CONTRACT RESULT
    # =====================================================

    @property
    def contract_made(self):

        required = self.tricks_required

        if (
            required is None
            or not self.is_complete
        ):

            return None

        return (
            self.declarer_tricks
            >= required
        )

    @property
    def result_text(self):

        required = self.tricks_required

        if (
            required is None
            or not self.is_complete
        ):

            return "—"

        difference = (
            self.declarer_tricks
            - required
        )

        if difference == 0:

            return "Made exactly"

        if difference > 0:

            return f"Made +{difference}"

        return f"Down {abs(difference)}"

    # =====================================================
    # SCORE
    # =====================================================

    def calculate_score(self):

        if not self.is_complete:

            return None

        if self.contract is None:

            return None

        from game_logic.scoring import (
            calculate_score
        )

        self.final_score = calculate_score(
            contract=self.contract,
            declarer=self.declarer,
            tricks_made=self.declarer_tricks,
            vulnerable=self.vulnerable,
            doubled=self.doubled,
        )

        self.result = self.result_text

        return self.final_score

    # =====================================================
    # DISPLAY HELPERS
    # =====================================================

    def contract_text(self):

        if self.contract is None:

            return "No Contract"

        level = getattr(
            self.contract,
            "level",
            "?",
        )

        denomination = getattr(
            self.contract,
            "denomination",
            None,
        )

        short = getattr(
            denomination,
            "short",
            "?",
        )

        declarer = getattr(
            self.contract,
            "declarer",
            self.declarer,
        )

        declarer_letter = (
            declarer.value
            if declarer is not None
            else "?"
        )

        return (
            f"{level}{short} "
            f"by {declarer_letter}"
        )