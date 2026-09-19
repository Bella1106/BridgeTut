"""
Stores the history of a single BridgeTut game.

A GameRecord contains:

- Game information
- Bidding information
- Notes
- All played tricks
- Trick winners
- Scoring information
- BBO makeable-tricks reference data
"""

from datetime import datetime

from bidding.bidding_system import SpecialCall

from game_logic.vulnerability import (
    determine_vulnerability,
    is_vulnerable,
)


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
        board_number=None,
        doubled=False,
        doubling_state=None,
        makeable_tricks=None,
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

        self.board_number = board_number

        self.makeable_tricks = (
            makeable_tricks
        )

        # =================================================
        # DOUBLING
        # =================================================

        if doubling_state is None:

            if doubled:

                self.doubling_state = (
                    SpecialCall.DOUBLE
                )

            else:

                self.doubling_state = None

        else:

            self.doubling_state = (
                doubling_state
            )

        self.doubled = (
            self.doubling_state
            == SpecialCall.DOUBLE
        )

        # =================================================
        # PERSISTENCE
        # =================================================

        self._on_change = None

        # =================================================
        # PLAY HISTORY
        # =================================================

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

        # -------------------------------------------------
        # BACKWARDS COMPATIBILITY
        # -------------------------------------------------

        if not hasattr(
            self,
            "doubling_state",
        ):

            if getattr(
                self,
                "doubled",
                False,
            ):

                self.doubling_state = (
                    SpecialCall.DOUBLE
                )

            else:

                self.doubling_state = None

        if not hasattr(
            self,
            "makeable_tricks",
        ):

            self.makeable_tricks = None

        self.doubled = (
            self.doubling_state
            == SpecialCall.DOUBLE
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

            return (
                f"Made +{difference}"
            )

        return (
            f"Down {abs(difference)}"
        )

    # =====================================================
    # VULNERABILITY
    # =====================================================

    @property
    def vulnerability(self):

        "the vulnerability printed on this board"

        return determine_vulnerability(
            getattr(
                self,
                "board_number",
                None,
            )
        )

    @property
    def declarer_vulnerable(self):

        "whether the declaring partnership is vulnerable"

        if self.declarer is None:

            return False

        return is_vulnerable(
            self.vulnerability,
            self.declarer,
        )

    # =====================================================
    # DOUBLING INFORMATION
    # =====================================================

    @property
    def doubling_text(self):

        if (
            self.doubling_state
            == SpecialCall.REDOUBLE
        ):

            return "Redoubled"

        if (
            self.doubling_state
            == SpecialCall.DOUBLE
        ):

            return "Doubled"

        return "Undoubled"

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
            vulnerable=self.declarer_vulnerable,
            doubled=self.doubled,
            doubling_state=self.doubling_state,
        )

        self.result = self.result_text

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

        self.final_score = None

        self.result = None

        self._notify_change()

        return removed_trick