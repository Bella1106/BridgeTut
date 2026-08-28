"""
Manages completed and in-progress BridgeTut games.

HistoryManager is responsible for creating, storing,
retrieving and deleting completed GameRecord objects.
"""

from .game_record import GameRecord


class HistoryManager:

    def __init__(self):

        self.games = []

        self.next_game_id = 1

    # =====================================================
    # ADD COMPLETED GAME
    # =====================================================

    def add_game(
        self,
        dealer,
        players,
        contract=None,
        declarer=None,
        bidding_history=None,
        notes="",
    ):

        game = GameRecord(
            game_id=self.next_game_id,
            dealer=dealer,
            players=players,
            contract=contract,
            declarer=declarer,
            bidding_history=bidding_history,
            notes=notes,
        )

        self.games.append(game)

        self.next_game_id += 1

        return game

    # =====================================================
    # GET ALL GAMES
    # =====================================================

    def get_games(self):

        # Newest games first.

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