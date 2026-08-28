"""
Stores the history of a single BridgeTut game.

A GameRecord contains:

- Game information
- Bidding information
- Notes
- All 13 played tricks

At this stage:

- Trick winners are NOT calculated.
- Final scoring is NOT calculated.
- Result is NOT calculated.

The Play page simply records the four cards played
in each trick.
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

        # =================================================
        # PLAY HISTORY
        # =================================================

        # Each item represents one completed trick.
        #
        # Example:
        #
        # {
        #     "trick_number": 1,
        #     "plays": [
        #         (Position.NORTH, card),
        #         (Position.EAST, card),
        #         (Position.SOUTH, card),
        #         (Position.WEST, card),
        #     ]
        # }
        #
        # Trick winners are intentionally not stored yet.

        self.tricks = []

        # =================================================
        # FUTURE SCORING
        # =================================================

        # These will be populated later when scoring
        # and trick resolution are implemented.

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
    ):

        """
        Store one completed trick.

        Parameters
        ----------
        trick_number : int
            Number of the trick, from 1 to 13.

        plays : dict
            Dictionary mapping Position -> Card.

        Example:

            {
                Position.NORTH: card,
                Position.EAST: card,
                Position.SOUTH: card,
                Position.WEST: card,
            }
        """

        trick = {
            "trick_number": trick_number,
            "plays": dict(plays),
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