import tempfile
import unittest
from pathlib import Path

from game_history.game_record import GameRecord
from game_history.history_manager import HistoryManager


class TestGameRecord(unittest.TestCase):

    # =====================================================
    # GAME RECORD CREATION
    # =====================================================

    def test_game_record_creation(self):

        game = GameRecord(
            game_id=1,
            dealer=None,
            players=[],
        )

        self.assertEqual(
            game.game_id,
            1,
        )

        self.assertIsNone(
            game.contract,
        )

        self.assertIsNone(
            game.declarer,
        )

        self.assertEqual(
            game.bidding_history,
            [],
        )

        self.assertEqual(
            game.notes,
            "",
        )

        self.assertEqual(
            game.tricks,
            [],
        )

        self.assertIsNone(
            game.final_score,
        )

        self.assertIsNone(
            game.result,
        )

    # =====================================================
    # NOTES
    # =====================================================

    def test_set_notes(self):

        game = GameRecord(
            game_id=1,
            dealer=None,
            players=[],
        )

        game.set_notes(
            "Good bidding practice."
        )

        self.assertEqual(
            game.notes,
            "Good bidding practice.",
        )

    # =====================================================
    # ADD TRICK
    # =====================================================

    def test_add_trick(self):

        game = GameRecord(
            game_id=1,
            dealer=None,
            players=[],
        )

        plays = {
            "North": "AS",
            "East": "KH",
            "South": "2C",
            "West": "JD",
        }

        game.add_trick(
            trick_number=1,
            plays=plays,
        )

        self.assertEqual(
            len(game.tricks),
            1,
        )

        self.assertEqual(
            game.tricks[0]["trick_number"],
            1,
        )

        self.assertEqual(
            game.tricks[0]["plays"],
            plays,
        )

    # =====================================================
    # TRICKS PLAYED
    # =====================================================

    def test_tricks_played(self):

        game = GameRecord(
            game_id=1,
            dealer=None,
            players=[],
        )

        for number in range(1, 4):

            game.add_trick(
                trick_number=number,
                plays={},
            )

        self.assertEqual(
            game.tricks_played,
            3,
        )

    # =====================================================
    # GAME COMPLETION
    # =====================================================

    def test_game_is_not_complete_before_13_tricks(self):

        game = GameRecord(
            game_id=1,
            dealer=None,
            players=[],
        )

        for number in range(1, 13):

            game.add_trick(
                trick_number=number,
                plays={},
            )

        self.assertFalse(
            game.is_complete,
        )

    def test_game_is_complete_after_13_tricks(self):

        game = GameRecord(
            game_id=1,
            dealer=None,
            players=[],
        )

        for number in range(1, 14):

            game.add_trick(
                trick_number=number,
                plays={},
            )

        self.assertTrue(
            game.is_complete,
        )


class TestHistoryManager(unittest.TestCase):

    def setUp(self):
        """
        Give every test its own temporary history file.

        This prevents the tests from reading or modifying the
        application's real game_history/history.pkl file.
        """

        self.temp_directory = tempfile.TemporaryDirectory()

        self.original_history_file = HistoryManager.HISTORY_FILE

        HistoryManager.HISTORY_FILE = (
            Path(self.temp_directory.name) / "history.pkl"
        )

    def tearDown(self):
        """
        Restore the real history file location after each test.
        """

        HistoryManager.HISTORY_FILE = self.original_history_file

        self.temp_directory.cleanup()

    # =====================================================
    # INITIAL STATE
    # =====================================================

    def test_history_manager_starts_empty(self):

        manager = HistoryManager()

        self.assertEqual(
            manager.get_games(),
            [],
        )

        self.assertIsNone(
            manager.get_latest_game(),
        )

    # =====================================================
    # ADD GAME
    # =====================================================

    def test_add_game(self):

        manager = HistoryManager()

        game = manager.add_game(
            dealer=None,
            players=[],
        )

        self.assertEqual(
            len(manager.games),
            1,
        )

        self.assertEqual(
            game.game_id,
            1,
        )

    # =====================================================
    # GAME IDS
    # =====================================================

    def test_game_ids_increment(self):

        manager = HistoryManager()

        game1 = manager.add_game(
            dealer=None,
            players=[],
        )

        game2 = manager.add_game(
            dealer=None,
            players=[],
        )

        game3 = manager.add_game(
            dealer=None,
            players=[],
        )

        self.assertEqual(
            game1.game_id,
            1,
        )

        self.assertEqual(
            game2.game_id,
            2,
        )

        self.assertEqual(
            game3.game_id,
            3,
        )

    # =====================================================
    # GET GAME
    # =====================================================

    def test_get_game(self):

        manager = HistoryManager()

        game = manager.add_game(
            dealer=None,
            players=[],
        )

        found_game = manager.get_game(
            game.game_id
        )

        self.assertIs(
            found_game,
            game,
        )

    def test_get_nonexistent_game(self):

        manager = HistoryManager()

        result = manager.get_game(
            999
        )

        self.assertIsNone(
            result,
        )

    # =====================================================
    # GET ALL GAMES
    # =====================================================

    def test_get_games_returns_newest_first(self):

        manager = HistoryManager()

        game1 = manager.add_game(
            dealer=None,
            players=[],
        )

        game2 = manager.add_game(
            dealer=None,
            players=[],
        )

        game3 = manager.add_game(
            dealer=None,
            players=[],
        )

        games = manager.get_games()

        self.assertEqual(
            games,
            [
                game3,
                game2,
                game1,
            ],
        )

    # =====================================================
    # LATEST GAME
    # =====================================================

    def test_get_latest_game(self):

        manager = HistoryManager()

        game1 = manager.add_game(
            dealer=None,
            players=[],
        )

        game2 = manager.add_game(
            dealer=None,
            players=[],
        )

        self.assertIs(
            manager.get_latest_game(),
            game2,
        )

    # =====================================================
    # DELETE GAME
    # =====================================================

    def test_delete_game(self):

        manager = HistoryManager()

        game1 = manager.add_game(
            dealer=None,
            players=[],
        )

        game2 = manager.add_game(
            dealer=None,
            players=[],
        )

        manager.delete_game(
            game1.game_id
        )

        self.assertIsNone(
            manager.get_game(
                game1.game_id
            )
        )

        self.assertIs(
            manager.get_game(
                game2.game_id
            ),
            game2,
        )

    # =====================================================
    # DELETE NONEXISTENT GAME
    # =====================================================

    def test_delete_nonexistent_game(self):

        manager = HistoryManager()

        manager.add_game(
            dealer=None,
            players=[],
        )

        # Should not crash.
        manager.delete_game(
            999
        )

        self.assertEqual(
            len(manager.games),
            1,
        )

    # =====================================================
    # GAME WITH NOTES
    # =====================================================

    def test_add_game_with_notes(self):

        manager = HistoryManager()

        game = manager.add_game(
            dealer=None,
            players=[],
            notes="Practice game.",
        )

        self.assertEqual(
            game.notes,
            "Practice game.",
        )


if __name__ == "__main__":
    unittest.main()