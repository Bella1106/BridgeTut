"""
undo_manager.py
---------------
Handles undo operations during the BridgeTut playing phase.

Undo works one card at a time.

The UndoManager does not store snapshots of the game.
Instead, it uses the current PlayPage state and the
committed GameRecord history to reconstruct the previous
state.

Responsibilities:

- Undo the latest card in the current trick.
- Reopen the latest completed trick when necessary.
- Return undone cards to players' hands.
- Restore the correct current player.
- Remove an undone completed trick from GameRecord.
- Reset the score when the game state changes.
"""


class UndoManager:

    # =====================================================
    # UNDO LAST PLAY
    # =====================================================

    @staticmethod
    def undo_last_play(
        players,
        played_cards,
        current_player,
        trick_number,
        trick_winner,
        game_record,
        game_complete,
    ):
        """
        Undo exactly one card play.

        Returns
        -------
        dict | None
            Updated play state.

            Returns None when there is nothing to undo.

        The returned dictionary contains:

            current_player
            played_cards
            trick_number
            trick_winner
            game_complete
        """

        # =================================================
        # CASE 1
        # =================================================
        # There are cards currently visible in the trick.
        #
        # Remove the most recently played card.
        # =================================================

        if played_cards:

            # Python dictionaries preserve insertion order.
            # The final key is therefore the player who
            # played the most recent card.

            last_player = (
                next(
                    reversed(
                        played_cards
                    )
                )
            )

            last_card = (
                played_cards[
                    last_player
                ]
            )

            # Return the card to the player's hand.

            players[
                last_player
            ].hand.add(
                last_card
            )

            # Make a copy before removing the card.

            updated_played_cards = dict(
                played_cards
            )

            updated_played_cards.pop(
                last_player
            )

            # =================================================
            # COMPLETED TRICK
            # =================================================
            #
            # If four cards were present, the trick has already
            # been committed to GameRecord.
            #
            # Undo removes that completed trick from history
            # and leaves the first three cards on the table.
            # =================================================

            if len(played_cards) == 4:

                if (
                    game_record is not None
                    and game_record.tricks
                ):

                    game_record.remove_last_trick()

                return {
                    "current_player": last_player,

                    "played_cards": (
                        updated_played_cards
                    ),

                    "trick_number": trick_number,

                    "trick_winner": None,

                    "game_complete": False,
                }

            # =================================================
            # UNFINISHED TRICK
            # =================================================

            return {
                "current_player": last_player,

                "played_cards": (
                    updated_played_cards
                ),

                "trick_number": trick_number,

                "trick_winner": trick_winner,

                "game_complete": game_complete,
            }

        # =================================================
        # CASE 2
        # =================================================
        # The current trick is empty.
        #
        # This happens after a completed trick has been
        # cleared and the next trick has started.
        #
        # Reopen the previous completed trick and undo its
        # final card.
        # =================================================

        if (
            game_record is None
            or not game_record.tricks
        ):

            return None

        last_trick = (
            game_record.tricks[-1]
        )

        plays = dict(
            last_trick.get(
                "plays",
                {},
            )
        )

        if not plays:

            return None

        # Dictionary insertion order preserves the order
        # in which the four cards were originally played.

        play_order = list(
            plays.keys()
        )

        # The last player in the sequence made the card
        # that we are undoing.

        last_player = play_order[-1]

        last_card = plays[
            last_player
        ]

        # Return the undone card to its owner's hand.

        players[
            last_player
        ].hand.add(
            last_card
        )

        # Remove the completed trick from permanent history.

        game_record.remove_last_trick()

        # Reopen the trick with the first three cards.

        reopened_trick = {}

        for player in play_order[:-1]:

            reopened_trick[
                player
            ] = plays[player]

        reopened_trick_number = (
            last_trick.get(
                "trick_number",
                trick_number,
            )
        )

        return {
            "current_player": last_player,

            "played_cards": reopened_trick,

            "trick_number": (
                reopened_trick_number
            ),

            "trick_winner": None,

            "game_complete": False,
        }