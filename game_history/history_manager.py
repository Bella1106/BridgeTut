"""
Manages completed and in-progress BridgeTut games.

HistoryManager is responsible for:

- Creating games
- Storing games
- Retrieving games
- Deleting games
- Saving games to disk
- Loading games from disk

The history is stored locally so it is not lost
when the BridgeTut application is closed.
"""

from pathlib import Path
import pickle

from .game_record import GameRecord


class HistoryManager:

    HISTORY_FILE = (
        Path(__file__).resolve().parent
        / "history.pkl"
    )

    def __init__(self):

        self.games = []

        self.next_game_id = 1

        print(
            f"History file: {self.HISTORY_FILE}"
        )

        self.load_history()

        print(
            f"Loaded games: {len(self.games)}"
        )

    # =====================================================
    # SAVE HISTORY
    # =====================================================

    def save_history(self):
        """
        Save all games and the next game ID to disk.
        """

        data = {
            "games": self.games,
            "next_game_id": self.next_game_id,
        }

        try:

            with open(
                self.HISTORY_FILE,
                "wb",
            ) as file:

                pickle.dump(
                    data,
                    file,
                )

        except OSError as error:

            print(
                f"Could not save game history: {error}"
            )

    # =====================================================
    # LOAD HISTORY
    # =====================================================

    def load_history(self):
        """
        Load previously saved games from disk.

        If no history file exists, BridgeTut
        simply starts with an empty history.
        """

        if not self.HISTORY_FILE.exists():

            return

        try:

            with open(
                self.HISTORY_FILE,
                "rb",
            ) as file:

                data = pickle.load(
                    file
                )

            self.games = data.get(
                "games",
                [],
            )

            self.next_game_id = data.get(
                "next_game_id",
                1,
            )

            for game in self.games:

                game.set_change_callback(
                    self.save_history
                )

        except (
            OSError,
            pickle.PickleError,
            EOFError,
        ) as error:

            print(
                f"Could not load game history: {error}"
            )

            self.games = []

            self.next_game_id = 1

    # =====================================================
    # ADD GAME
    # =====================================================

    def add_game(
        self,
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

        print(
            f"Adding game #{self.next_game_id}"
        )

        game = GameRecord(
            game_id=self.next_game_id,
            dealer=dealer,
            players=players,
            contract=contract,
            declarer=declarer,
            bidding_history=bidding_history,
            notes=notes,
            board_number=board_number,
            doubled=doubled,
            doubling_state=doubling_state,
            makeable_tricks=makeable_tricks,
        )

        game.set_change_callback(
            self.save_history
        )

        self.games.append(
            game
        )

        self.next_game_id += 1

        self.save_history()

        return game

    # =====================================================
    # GET ALL GAMES
    # =====================================================

    def get_games(self):

        return list(
            reversed(
                self.games
            )
        )

    # =====================================================
    # GET GAME
    # =====================================================

    def get_game(
        self,
        game_id,
    ):

        for game in self.games:

            if game.game_id == game_id:

                return game

        return None

    # =====================================================
    # GET LATEST GAME
    # =====================================================

    def get_latest_game(self):

        if not self.games:

            return None

        return self.games[-1]

    # =====================================================
    # DELETE GAME
    # =====================================================

    def delete_game(
        self,
        game_id,
    ):

        self.games = [
            game
            for game in self.games
            if game.game_id != game_id
        ]

        self.save_history()