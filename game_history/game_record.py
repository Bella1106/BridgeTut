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
        # PERSISTENCE
        # =================================================

        # HistoryManager sets this callback when the
        # GameRecord is created or loaded.
        #
        # It is used to save the history whenever
        # something in this game changes.

        self._on_change = None

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
    # PERSISTENCE CALLBACK
    # =====================================================

    def set_change_callback(
        self,
        callback,
    ):
        """
        Set the function that should be called
        whenever this game changes.
        """

        self._on_change = callback

    def _notify_change(self):
        """
        Notify HistoryManager that this game
        has changed and should be saved.
        """

        if self._on_change is not None:

            self._on_change()

    # =====================================================
    # PICKLE SUPPORT
    # =====================================================

    def __getstate__(self):
        """
        Prepare the GameRecord for saving with pickle.

        The callback is not saved because it points back
        to the HistoryManager. It will be restored by
        HistoryManager when the record is loaded.
        """

        state = self.__dict__.copy()

        state["_on_change"] = None

        return state

    def __setstate__(
        self,
        state,
    ):
        """
        Restore the GameRecord when loading from pickle.

        HistoryManager will reconnect the change callback
        after loading.
        """

        self.__dict__.update(
            state
        )

        self._on_change = None

    # =====================================================
    # NOTES
    # =====================================================

    def set_notes(
        self,
        notes,
    ):

        self.notes = notes

        # Save the updated notes.

        self._notify_change()

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

        # Save the updated trick history.

        self._notify_change()

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

        # Save the calculated score and result.

        self._notify_change()

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

        # =====================================================
    # REMOVE LAST TRICK
    # =====================================================

    def remove_last_trick(self):
        """
        Remove the most recently completed trick.

        Used by the Play phase when a completed trick
        is undone.
        """

        if not self.tricks:

            return None

        removed_trick = (
            self.tricks.pop()
        )

        # The previously calculated score is no longer valid
        # because the game state has changed.

        self.final_score = None

        self.result = None

        self._notify_change()

        return removed_trick