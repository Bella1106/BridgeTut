from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QFrame,
    QScrollArea,
    QMessageBox,
)

from bidding.bidding_system import SpecialCall


class HistoryPage(QWidget):

    def __init__(
        self,
        history_manager,
        parent=None,
    ):

        super().__init__(parent)

        self.history_manager = history_manager

        self.selected_game = None

        self.game_list = None
        self.game_title = None
        self.game_result = None
        self.game_score = None
        self.game_details = None
        self.notes_edit = None
        self.tricks_container = None
        self.tricks_layout = None

        self.delete_button = None

        self.setup_ui()

        self.refresh_history()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        main_layout = QHBoxLayout(self)

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        main_layout.setSpacing(16)

        # =================================================
        # LEFT PANEL
        # =================================================

        left_panel = QFrame()

        left_panel.setObjectName(
            "historyPanel"
        )

        left_layout = QVBoxLayout(
            left_panel
        )

        left_layout.setContentsMargins(
            16,
            16,
            16,
            16,
        )

        title = QLabel(
            "GAME HISTORY"
        )

        title.setObjectName(
            "historyTitle"
        )

        left_layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Previously played games"
        )

        subtitle.setObjectName(
            "historySubtitle"
        )

        left_layout.addWidget(
            subtitle
        )

        self.game_list = QListWidget()

        self.game_list.setObjectName(
            "gameList"
        )

        self.game_list.currentItemChanged.connect(
            self.on_game_selected
        )

        left_layout.addWidget(
            self.game_list
        )

        main_layout.addWidget(
            left_panel,
            1,
        )

        # =================================================
        # RIGHT PANEL
        # =================================================

        right_panel = QFrame()

        right_panel.setObjectName(
            "historyPanel"
        )

        right_layout = QVBoxLayout(
            right_panel
        )

        right_layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )

        # -------------------------------------------------
        # GAME TITLE
        # -------------------------------------------------

        self.game_title = QLabel(
            "No game selected"
        )

        self.game_title.setObjectName(
            "selectedGameTitle"
        )

        right_layout.addWidget(
            self.game_title
        )

        # -------------------------------------------------
        # GAME RESULT
        # -------------------------------------------------

        self.game_result = QLabel()

        self.game_result.setObjectName(
            "gameResult"
        )

        right_layout.addWidget(
            self.game_result
        )

        # -------------------------------------------------
        # GAME SCORE
        # -------------------------------------------------

        self.game_score = QLabel()

        self.game_score.setObjectName(
            "gameScore"
        )

        right_layout.addWidget(
            self.game_score
        )

        # -------------------------------------------------
        # GAME DETAILS
        # -------------------------------------------------

        self.game_details = QLabel()

        self.game_details.setObjectName(
            "gameDetails"
        )

        self.game_details.setWordWrap(
            True
        )

        right_layout.addWidget(
            self.game_details
        )

        # =================================================
        # TRICK HISTORY
        # =================================================

        tricks_title = QLabel(
            "TRICK HISTORY"
        )

        tricks_title.setObjectName(
            "sectionTitle"
        )

        right_layout.addWidget(
            tricks_title
        )

        # -------------------------------------------------
        # SCROLL AREA
        # -------------------------------------------------

        scroll = QScrollArea()

        scroll.setObjectName(
            "trickScroll"
        )

        scroll.setWidgetResizable(
            True
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.tricks_container = QWidget()

        self.tricks_layout = QVBoxLayout(
            self.tricks_container
        )

        self.tricks_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.tricks_layout.setSpacing(
            8
        )

        scroll.setWidget(
            self.tricks_container
        )

        right_layout.addWidget(
            scroll,
            2,
        )

        # =================================================
        # NOTES
        # =================================================

        notes_title = QLabel(
            "NOTES"
        )

        notes_title.setObjectName(
            "sectionTitle"
        )

        right_layout.addWidget(
            notes_title
        )

        self.notes_edit = QTextEdit()

        self.notes_edit.setPlaceholderText(
            "Add notes about this game..."
        )

        self.notes_edit.setObjectName(
            "notesEdit"
        )

        self.notes_edit.setMaximumHeight(
            100
        )

        right_layout.addWidget(
            self.notes_edit
        )

        # =================================================
        # NOTE ACTIONS
        # =================================================

        actions_layout = QHBoxLayout()

        actions_layout.setSpacing(
            10
        )

        # -------------------------------------------------
        # SAVE NOTES
        # -------------------------------------------------

        save_button = QPushButton(
            "Save Notes"
        )

        save_button.setObjectName(
            "saveButton"
        )

        save_button.setCursor(
            Qt.PointingHandCursor
        )

        save_button.clicked.connect(
            self.save_notes
        )

        actions_layout.addWidget(
            save_button
        )

        # -------------------------------------------------
        # DELETE GAME
        # -------------------------------------------------

        self.delete_button = QPushButton(
            "Delete Game"
        )

        self.delete_button.setObjectName(
            "deleteButton"
        )

        self.delete_button.setCursor(
            Qt.PointingHandCursor
        )

        self.delete_button.clicked.connect(
            self.delete_selected_game
        )

        self.delete_button.setEnabled(
            False
        )

        actions_layout.addWidget(
            self.delete_button
        )

        right_layout.addLayout(
            actions_layout
        )

        # -------------------------------------------------
        # ADD RIGHT PANEL
        # -------------------------------------------------

        main_layout.addWidget(
            right_panel,
            2,
        )

        # -------------------------------------------------
        # STYLE
        # -------------------------------------------------

        self.setStyleSheet(
            self.get_style()
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_history(self):

        self.game_list.clear()

        games = (
            self.history_manager.get_games()
        )

        for game in games:

            item = QListWidgetItem(
                f"Game #{game.game_id}"
            )

            item.setData(
                Qt.UserRole,
                game.game_id
            )

            self.game_list.addItem(
                item
            )

        if not games:

            self.show_no_games()

            return

        # -------------------------------------------------
        # AUTOMATICALLY SELECT LATEST GAME
        # -------------------------------------------------

        self.game_list.setCurrentRow(
            0
        )

    # =====================================================
    # SELECT GAME
    # =====================================================

    def on_game_selected(
        self,
        current,
        previous,
    ):

        if current is None:

            self.show_no_games()

            return

        game_id = current.data(
            Qt.UserRole
        )

        game = (
            self.history_manager.get_game(
                game_id
            )
        )

        if game is None:

            return

        self.selected_game = game

        self.display_game(
            game
        )

        # Enable delete button.

        if self.delete_button is not None:

            self.delete_button.setEnabled(
                True
            )

    # =====================================================
    # DISPLAY GAME
    # =====================================================

    def display_game(
        self,
        game,
    ):

        self.game_title.setText(
            f"Game #{game.game_id}"
        )

        # -------------------------------------------------
        # GAME WINNER
        # -------------------------------------------------

        winner_text = (
            self.get_game_winner(
                game
            )
        )

        self.game_result.setText(
            f"<b>Winner:</b> {winner_text}"
        )

        # -------------------------------------------------
        # FINAL SCORE
        # -------------------------------------------------

        score = game.final_score

        if score is None:

            # Calculate the score if the game
            # has already been completed but
            # the score has not yet been calculated.

            if game.is_complete:

                score = (
                    game.calculate_score()
                )

        if score is None:

            score_text = (
                "<b>Final Score:</b> "
                "Not available"
            )

        else:

            ns_score = score
            ew_score = -score

            ns_text = (
                f"+{ns_score}"
                if ns_score > 0
                else str(ns_score)
            )

            ew_text = (
                f"+{ew_score}"
                if ew_score > 0
                else str(ew_score)
            )

            score_text = (
                "<b>Final Score:</b><br>"
                f"North / South: {ns_text}<br>"
                f"East / West: {ew_text}"
            )

        self.game_score.setText(
            score_text
        )

        # -------------------------------------------------
        # GAME DETAILS
        # -------------------------------------------------

        dealer = self.position_name(
            game.dealer
        )

        declarer = self.position_name(
            game.declarer
        )

        contract = game.contract_text()

        doubling = self.get_doubling_text(
            game
        )

        vulnerability = self.vulnerability_text(
            game
        )

        # -------------------------------------------------
        # GAME OUTCOME
        # -------------------------------------------------

        outcome = getattr(
            game,
            "result",
            None,
        )

        if outcome is None:

            outcome = game.result_text

        details = (
            f"<b>Dealer:</b> {dealer}<br>"
            f"<b>Contract:</b> {contract}<br>"
            f"<b>Declarer:</b> {declarer}<br>"
            f"<b>Doubling:</b> {doubling}<br>"
            f"<b>Vulnerability:</b> "
            f"{vulnerability}<br>"
            f"<b>Result:</b> {outcome}<br>"
            f"<b>Bids:</b> "
            f"{len(game.bidding_history)}<br>"
            f"<b>Tricks:</b> "
            f"{game.tricks_played} / 13"
        )

        self.game_details.setText(
            details
        )

        self.display_tricks(
            game
        )

        self.notes_edit.setPlainText(
            game.notes
        )

    # =====================================================
    # DOUBLING TEXT
    # =====================================================

    @staticmethod
    def get_doubling_text(
        game,
    ):
        """
        Return the doubling state for display.

        Supports the new doubling_state field while
        remaining compatible with older saved games.
        """

        doubling_state = getattr(
            game,
            "doubling_state",
            None,
        )

        if doubling_state == SpecialCall.REDOUBLE:

            return "Redoubled"

        if doubling_state == SpecialCall.DOUBLE:

            return "Doubled"

        # -------------------------------------------------
        # BACKWARDS COMPATIBILITY
        # -------------------------------------------------

        if getattr(
            game,
            "doubled",
            False,
        ):

            return "Doubled"

        return "Undoubled"

    # =====================================================
    # VULNERABILITY TEXT
    # =====================================================

    @staticmethod
    def vulnerability_text(
        game,
    ):
        """
        Return the vulnerability stored for the game.

        GameRecord determines vulnerability from the
        board number.
        """

        vulnerability = getattr(
            game,
            "vulnerability",
            None,
        )

        if vulnerability is None:

            return "Unknown"

        return str(
            vulnerability
        )

    # =====================================================
    # DETERMINE GAME WINNER
    # =====================================================

    @staticmethod
    def get_game_winner(
        game,
    ):

        # -------------------------------------------------
        # If the game has not been completed,
        # there is no winner yet.
        # -------------------------------------------------

        if not game.is_complete:

            return "Game in progress"

        # -------------------------------------------------
        # Get the final score.
        #
        # Scores are stored from the NS perspective:
        #
        # Positive = North/South won
        # Negative = East/West won
        # Zero     = Draw
        # -------------------------------------------------

        score = game.final_score

        if score is None:

            score = (
                game.calculate_score()
            )

        if score > 0:

            return "North / South"

        if score < 0:

            return "East / West"

        return "Draw"

    # =====================================================
    # DISPLAY TRICKS
    # =====================================================

    def display_tricks(
        self,
        game,
    ):

        # -------------------------------------------------
        # CLEAR OLD TRICKS
        # -------------------------------------------------

        while self.tricks_layout.count():

            item = (
                self.tricks_layout.takeAt(
                    0
                )
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

        # -------------------------------------------------
        # NO TRICKS
        # -------------------------------------------------

        if not game.tricks:

            empty = QLabel(
                "No tricks have been played yet."
            )

            empty.setObjectName(
                "emptyTricks"
            )

            self.tricks_layout.addWidget(
                empty
            )

            return

        # -------------------------------------------------
        # DISPLAY EVERY TRICK
        # -------------------------------------------------

        for trick in game.tricks:

            trick_number = trick.get(
                "trick_number",
                "?",
            )

            plays = trick.get(
                "plays",
                {},
            )

            winner = trick.get(
                "winner"
            )

            trick_frame = QFrame()

            trick_frame.setObjectName(
                "trickFrame"
            )

            trick_layout = QVBoxLayout(
                trick_frame
            )

            trick_layout.setContentsMargins(
                12,
                10,
                12,
                10,
            )

            trick_layout.setSpacing(
                5
            )

            # ---------------------------------------------
            # TRICK TITLE
            # ---------------------------------------------

            title = QLabel(
                f"TRICK {trick_number}"
            )

            title.setObjectName(
                "trickTitle"
            )

            trick_layout.addWidget(
                title
            )

            # ---------------------------------------------
            # CARDS
            # ---------------------------------------------

            cards_layout = QHBoxLayout()

            cards_layout.setSpacing(
                18
            )

            display_order = [

                self.position_from_letter(
                    "N"
                ),

                self.position_from_letter(
                    "E"
                ),

                self.position_from_letter(
                    "S"
                ),

                self.position_from_letter(
                    "W"
                ),
            ]

            for position in display_order:

                if position not in plays:

                    continue

                card = plays[position]

                player_letter = (
                    self.position_letter(
                        position
                    )
                )

                card_text = self.card_text(
                    card
                )

                card_label = QLabel(
                    f"{player_letter}: "
                    f"{card_text}"
                )

                card_label.setObjectName(
                    "trickCard"
                )

                cards_layout.addWidget(
                    card_label
                )

            cards_layout.addStretch()

            trick_layout.addLayout(
                cards_layout
            )

            # ---------------------------------------------
            # TRICK WINNER
            # ---------------------------------------------

            winner_text = self.position_name(
                winner
            )

            winner_label = QLabel(
                f"<b>Winner:</b> "
                f"{winner_text}"
            )

            winner_label.setObjectName(
                "trickWinner"
            )

            trick_layout.addWidget(
                winner_label
            )

            self.tricks_layout.addWidget(
                trick_frame
            )

        self.tricks_layout.addStretch()

    # =====================================================
    # CARD TEXT
    # =====================================================

    @staticmethod
    def card_text(
        card,
    ):

        if card is None:

            return "—"

        rank = getattr(
            card.rank,
            "short",
            str(card.rank),
        )

        suit = getattr(
            card.suit,
            "symbol",
            str(card.suit),
        )

        return (
            f"{rank}{suit}"
        )

    # =====================================================
    # POSITION FROM LETTER
    # =====================================================

    @staticmethod
    def position_from_letter(
        letter,
    ):

        from card_model.player import Position

        mapping = {

            "N": Position.NORTH,

            "E": Position.EAST,

            "S": Position.SOUTH,

            "W": Position.WEST,
        }

        return mapping[letter]

    # =====================================================
    # SAVE NOTES
    # =====================================================

    def save_notes(self):

        if self.selected_game is None:

            return

        notes = (
            self.notes_edit.toPlainText()
        )

        self.selected_game.set_notes(
            notes
        )

        # -------------------------------------------------
        # CUSTOM CONFIRMATION MESSAGE BOX
        # -------------------------------------------------

        message_box = QMessageBox(
            self
        )

        message_box.setWindowTitle(
            "Notes Saved"
        )

        message_box.setText(
            "Notes saved successfully."
        )

        message_box.setIcon(
            QMessageBox.Information
        )

        message_box.setStandardButtons(
            QMessageBox.Ok
        )

        message_box.setStyleSheet("""

            QMessageBox {
                background-color: #11271d;
            }

            QMessageBox QLabel {
                color: #f1f4f2;
                font-size: 15px;
                padding: 10px;
            }

            QMessageBox QPushButton {
                background-color: #51b5ba;
                color: #071710;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                min-width: 70px;
                font-size: 14px;
                font-weight: bold;
            }

            QMessageBox QPushButton:hover {
                background-color: #68c4c8;
            }

            QMessageBox QPushButton:pressed {
                background-color: #3d9da2;
            }

        """)

        message_box.exec()

    # =====================================================
    # DELETE SELECTED GAME
    # =====================================================

    def delete_selected_game(self):

        if self.selected_game is None:

            return

        game_id = (
            self.selected_game.game_id
        )

        # -------------------------------------------------
        # CONFIRM DELETION
        # -------------------------------------------------

        message_box = QMessageBox(
            self
        )

        message_box.setWindowTitle(
            "Delete Game"
        )

        message_box.setText(
            f"Delete Game #{game_id}?"
        )

        message_box.setInformativeText(
            "This game record will be permanently "
            "removed from history."
        )

        message_box.setIcon(
            QMessageBox.Warning
        )

        message_box.setStandardButtons(
            QMessageBox.Yes
            | QMessageBox.No
        )

        message_box.setDefaultButton(
            QMessageBox.No
        )

        message_box.setStyleSheet("""

            QMessageBox {
                background-color: #11271d;
            }

            QMessageBox QLabel {
                color: #f1f4f2;
                font-size: 15px;
                padding: 10px;
            }

            QMessageBox QPushButton {
                background-color: #51b5ba;
                color: #071710;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                min-width: 70px;
                font-size: 14px;
                font-weight: bold;
            }

            QMessageBox QPushButton:hover {
                background-color: #68c4c8;
            }

            QMessageBox QPushButton:pressed {
                background-color: #3d9da2;
            }

        """)

        result = message_box.exec()

        if result != QMessageBox.Yes:

            return

        # -------------------------------------------------
        # DELETE FROM HISTORY MANAGER
        # -------------------------------------------------

        self.history_manager.delete_game(
            game_id
        )

        # -------------------------------------------------
        # CLEAR CURRENT SELECTION
        # -------------------------------------------------

        self.selected_game = None

        # -------------------------------------------------
        # DISABLE DELETE BUTTON
        # -------------------------------------------------

        if self.delete_button is not None:

            self.delete_button.setEnabled(
                False
            )

        # -------------------------------------------------
        # REFRESH HISTORY
        # -------------------------------------------------

        self.refresh_history()

    # =====================================================
    # NO GAMES
    # =====================================================

    def show_no_games(self):

        self.selected_game = None

        self.game_title.setText(
            "No game selected"
        )

        self.game_result.setText(
            ""
        )

        self.game_score.setText(
            ""
        )

        self.game_details.setText(
            "No games have been recorded yet."
        )

        self.notes_edit.clear()

        if self.delete_button is not None:

            self.delete_button.setEnabled(
                False
            )

        while self.tricks_layout.count():

            item = (
                self.tricks_layout.takeAt(
                    0
                )
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

    # =====================================================
    # POSITION
    # =====================================================

    @staticmethod
    def position_name(
        position,
    ):

        if position is None:

            return "—"

        return position.value.title()

    @staticmethod
    def position_letter(
        position,
    ):

        if position is None:

            return "?"

        return position.value.upper()

    # =====================================================
    # STYLE
    # =====================================================

    def get_style(self):

        return """

        QWidget {
            font-family: "Segoe UI", Arial, sans-serif;
        }

        QFrame#historyPanel {
            background-color: #11271d;
            border: 1px solid #29483b;
            border-radius: 10px;
        }

        QLabel {
            color: #f1f4f2;
        }

        QLabel#historyTitle {
            color: #e5c557;
            font-family: Georgia, serif;
            font-size: 23px;
            font-weight: bold;
        }

        QLabel#historySubtitle {
            color: #b9c8c1;
            font-size: 13px;
            padding-bottom: 10px;
        }

        QLabel#selectedGameTitle {
            color: #e5c557;
            font-family: Georgia, serif;
            font-size: 25px;
            font-weight: bold;
        }

        QLabel#gameResult {
            color: #51b5ba;
            font-size: 16px;
            font-weight: bold;
            padding-top: 3px;
        }

        QLabel#gameScore {
            color: #e5c557;
            font-size: 16px;
            font-weight: bold;
            padding-bottom: 3px;
        }

        QLabel#gameDetails {
            color: #d1dbd5;
            font-size: 14px;
            padding: 10px 0px;
        }

        QLabel#sectionTitle {
            color: #b9c8c1;
            font-size: 12px;
            letter-spacing: 1px;
        }

        QListWidget#gameList {
            background-color: #071710;
            border: 1px solid #29483b;
            border-radius: 6px;
            color: #f1f4f2;
            padding: 4px;
        }

        QListWidget#gameList::item {
            padding: 12px;
            border-radius: 5px;
        }

        QListWidget#gameList::item:selected {
            background-color: #51b5ba;
            color: #071710;
            font-weight: bold;
        }

        QScrollArea#trickScroll {
            background-color: transparent;
            border: none;
        }

        QFrame#trickFrame {
            background-color: #071710;
            border: 1px solid #29483b;
            border-radius: 7px;
        }

        QLabel#trickTitle {
            color: #e5c557;
            font-size: 13px;
            font-weight: bold;
        }

        QLabel#trickCard {
            color: #f1f4f2;
            font-size: 14px;
            font-weight: bold;
        }

        QLabel#trickWinner {
            color: #51b5ba;
            font-size: 13px;
            font-weight: bold;
            padding-top: 3px;
        }

        QLabel#emptyTricks {
            color: #8fa198;
            font-size: 13px;
            padding: 10px;
        }

        QTextEdit#notesEdit {
            background-color: #071710;
            color: #f1f4f2;
            border: 1px solid #29483b;
            border-radius: 6px;
            padding: 8px;
        }

        QPushButton#saveButton {
            background-color: #51b5ba;
            color: #071710;
            border: none;
            border-radius: 6px;
            padding: 11px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton#saveButton:hover {
            background-color: #68c4c8;
        }

        QPushButton#deleteButton {
            background-color: #11271d;
            color: #d87373;
            border: 1px solid #7a4040;
            border-radius: 6px;
            padding: 11px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton#deleteButton:hover {
            background-color: #3a2424;
            color: #f1aaaa;
            border: 1px solid #a95757;
        }

        QPushButton#deleteButton:pressed {
            background-color: #291b1b;
        }

        QPushButton#deleteButton:disabled {
            background-color: #11271d;
            color: #5f6964;
            border: 1px solid #29483b;
        }

        """