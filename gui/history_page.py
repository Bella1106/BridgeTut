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
        play_deal_callback=None,
        parent=None,
    ):
        super().__init__(parent)

        self.history_manager = history_manager

        self.play_deal_callback = play_deal_callback

        self.selected_game = None

        self.game_list = None
        self.game_title = None
        self.game_result = None
        self.game_score = None
        self.game_details = None
        self.notes_edit = None
        self.tricks_container = None
        self.tricks_layout = None

        self.makeable_tricks_container = None
        self.makeable_tricks_table = None

        self.play_deal_button = None
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

        right_layout.setSpacing(
            8
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

        # =================================================
        # GAME INFORMATION
        # =================================================

        game_info_frame = QFrame()

        game_info_frame.setObjectName(
            "gameInfoFrame"
        )

        game_info_layout = QHBoxLayout(
            game_info_frame
        )

        game_info_layout.setContentsMargins(
            0,
            4,
            0,
            6,
        )

        game_info_layout.setSpacing(
            30
        )

        # -------------------------------------------------
        # LEFT INFORMATION COLUMN
        # -------------------------------------------------

        left_info = QVBoxLayout()

        left_info.setSpacing(
            5
        )

        self.dealer_label = QLabel()
        self.dealer_label.setObjectName(
            "gameInfoLabel"
        )

        self.contract_label = QLabel()
        self.contract_label.setObjectName(
            "gameInfoLabel"
        )

        self.declarer_label = QLabel()
        self.declarer_label.setObjectName(
            "gameInfoLabel"
        )

        left_info.addWidget(
            self.dealer_label
        )

        left_info.addWidget(
            self.contract_label
        )

        left_info.addWidget(
            self.declarer_label
        )

        # -------------------------------------------------
        # RIGHT INFORMATION COLUMN
        # -------------------------------------------------

        right_info = QVBoxLayout()

        right_info.setSpacing(
            5
        )

        self.doubling_label = QLabel()
        self.doubling_label.setObjectName(
            "gameInfoLabel"
        )

        self.vulnerability_label = QLabel()
        self.vulnerability_label.setObjectName(
            "gameInfoLabel"
        )

        self.outcome_label = QLabel()
        self.outcome_label.setObjectName(
            "gameInfoLabel"
        )

        right_info.addWidget(
            self.doubling_label
        )

        right_info.addWidget(
            self.vulnerability_label
        )

        right_info.addWidget(
            self.outcome_label
        )

        game_info_layout.addLayout(
            left_info,
            1
        )

        game_info_layout.addLayout(
            right_info,
            1
        )

        right_layout.addWidget(
            game_info_frame
        )

        # -------------------------------------------------
        # BIDS / TRICKS SUMMARY
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
        # BBO MAKEABLE TRICKS
        # =================================================

        self.makeable_tricks_container = QFrame()

        self.makeable_tricks_container.setObjectName(
            "makeableTricksContainer"
        )

        makeable_layout = QVBoxLayout(
            self.makeable_tricks_container
        )

        makeable_layout.setContentsMargins(
            0,
            4,
            0,
            6,
        )

        makeable_layout.setSpacing(
            5
        )

        makeable_title = QLabel(
            "BBO MAKEABLE TRICKS"
        )

        makeable_title.setObjectName(
            "sectionTitle"
        )

        makeable_layout.addWidget(
            makeable_title
        )

        self.makeable_tricks_table = QFrame()

        self.makeable_tricks_table.setObjectName(
            "makeableTricksTable"
        )

        makeable_table_layout = QVBoxLayout(
            self.makeable_tricks_table
        )

        makeable_table_layout.setContentsMargins(
            8,
            5,
            8,
            5,
        )

        makeable_table_layout.setSpacing(
            1
        )

        makeable_layout.addWidget(
            self.makeable_tricks_table
        )

        right_layout.addWidget(
            self.makeable_tricks_container
        )

        self.makeable_tricks_container.hide()

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
        # ACTIONS
        # =================================================

        actions_layout = QHBoxLayout()

        actions_layout.setSpacing(
            10
        )

        # -------------------------------------------------
        # PLAY THIS DEAL
        # -------------------------------------------------

        self.play_deal_button = QPushButton(
            "Play This Deal"
        )

        self.play_deal_button.setObjectName(
            "playDealButton"
        )

        self.play_deal_button.setCursor(
            Qt.PointingHandCursor
        )

        self.play_deal_button.clicked.connect(
            self.play_selected_deal
        )

        self.play_deal_button.setEnabled(
            False
        )

        actions_layout.addWidget(
            self.play_deal_button
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

        main_layout.addWidget(
            right_panel,
            2,
        )

        self.setStyleSheet(
            self.get_style()
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_history(self):

        self.selected_game = None

        self.game_list.blockSignals(
            True
        )

        self.game_list.clear()

        games = (
            self.history_manager.get_games()
        )

        for game in games:

            status = ""

            if not game.is_complete:

                status = " (In Progress)"

            item = QListWidgetItem(
                f"Game #{game.game_id}{status}"
            )

            item.setData(
                Qt.UserRole,
                game.game_id
            )

            self.game_list.addItem(
                item
            )

        self.game_list.blockSignals(
            False
        )

        if not games:

            self.show_no_games()

            return

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

            self.show_no_games()

            return

        self.selected_game = game

        self.display_game(
            game
        )

        self.delete_button.setEnabled(
            True
        )

        self.play_deal_button.setEnabled(
            True
        )

    # =====================================================
    # PLAY SELECTED DEAL
    # =====================================================

    def play_selected_deal(self):

        if self.selected_game is None:

            return

        if self.play_deal_callback is None:

            return

        self.play_deal_callback(
            self.selected_game
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

        winner_text = (
            self.get_game_winner(
                game
            )
        )

        self.game_result.setText(
            f"<b>Winner:</b> {winner_text}"
        )

        score = game.final_score

        if score is None:

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
                "<b>Final Score:</b> "
                f"North / South: {ns_text}  |  "
                f"East / West: {ew_text}"
            )

        self.game_score.setText(
            score_text
        )

        # -------------------------------------------------
        # GAME INFORMATION
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

        outcome = getattr(
            game,
            "result",
            None,
        )

        if outcome is None:

            outcome = getattr(
                game,
                "result_text",
                "—",
            )

        self.dealer_label.setText(
            f"<b>Dealer:</b> {dealer}"
        )

        self.contract_label.setText(
            f"<b>Contract:</b> {contract}"
        )

        self.declarer_label.setText(
            f"<b>Declarer:</b> {declarer}"
        )

        self.doubling_label.setText(
            f"<b>Doubling:</b> {doubling}"
        )

        self.vulnerability_label.setText(
            f"<b>Vulnerability:</b> "
            f"{vulnerability}"
        )

        self.outcome_label.setText(
            f"<b>Result:</b> {outcome}"
        )

        self.game_details.setText(
            f"<b>Bids:</b> "
            f"{len(game.bidding_history)}"
            f" &nbsp;&nbsp; "
            f"<b>Tricks:</b> "
            f"{game.tricks_played} / 13"
        )

        self.display_makeable_tricks(
            game
        )

        self.display_tricks(
            game
        )

        self.notes_edit.setPlainText(
            getattr(
                game,
                "notes",
                "",
            )
        )

    # =====================================================
    # DISPLAY BBO MAKEABLE TRICKS
    # =====================================================

    def display_makeable_tricks(
        self,
        game,
    ):

        makeable_tricks = getattr(
            game,
            "makeable_tricks",
            None,
        )

        if not makeable_tricks:

            self.makeable_tricks_container.hide()

            return

        layout = (
            self.makeable_tricks_table.layout()
        )

        while layout.count():

            item = layout.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

            child_layout = item.layout()

            if child_layout is not None:

                while child_layout.count():

                    child_item = (
                        child_layout.takeAt(
                            0
                        )
                    )

                    child_widget = (
                        child_item.widget()
                    )

                    if child_widget is not None:

                        child_widget.deleteLater()

        header_layout = QHBoxLayout()

        header_layout.setSpacing(
            4
        )

        header_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        corner = QLabel("")

        corner.setObjectName(
            "makeableHeader"
        )

        corner.setFixedWidth(
            70
        )

        header_layout.addWidget(
            corner
        )

        denominations = [
            ("♣", "C"),
            ("♦", "D"),
            ("♥", "H"),
            ("♠", "S"),
            ("NT", "NT"),
        ]

        for symbol, denomination in denominations:

            label = QLabel(
                symbol
            )

            label.setObjectName(
                "makeableHeader"
            )

            label.setAlignment(
                Qt.AlignCenter
            )

            header_layout.addWidget(
                label,
                1
            )

        layout.addLayout(
            header_layout
        )

        positions = [
            ("North", "N"),
            ("East", "E"),
            ("South", "S"),
            ("West", "W"),
        ]

        for position_name, position_key in positions:

            row_layout = QHBoxLayout()

            row_layout.setSpacing(
                4
            )

            row_layout.setContentsMargins(
                0,
                0,
                0,
                0,
            )

            position_label = QLabel(
                position_name
            )

            position_label.setObjectName(
                "makeablePosition"
            )

            position_label.setFixedWidth(
                70
            )

            row_layout.addWidget(
                position_label
            )

            values = self.get_makeable_position_values(
                makeable_tricks,
                position_key,
            )

            for _, denomination in denominations:

                value = self.get_makeable_value(
                    values,
                    denomination,
                )

                value_text = (
                    "—"
                    if value is None
                    else str(value)
                )

                value_label = QLabel(
                    value_text
                )

                value_label.setObjectName(
                    "makeableValue"
                )

                value_label.setAlignment(
                    Qt.AlignCenter
                )

                row_layout.addWidget(
                    value_label,
                    1
                )

            layout.addLayout(
                row_layout
            )

        self.makeable_tricks_container.show()

    # =====================================================
    # GET MAKEABLE POSITION VALUES
    # =====================================================

    @staticmethod
    def get_makeable_position_values(
        makeable_tricks,
        position_key,
    ):

        if not isinstance(
            makeable_tricks,
            dict,
        ):

            return {}

        values = makeable_tricks.get(
            position_key
        )

        if isinstance(
            values,
            dict,
        ):

            return values

        try:

            from card_model.player import Position

            position_mapping = {
                "N": Position.NORTH,
                "E": Position.EAST,
                "S": Position.SOUTH,
                "W": Position.WEST,
            }

            enum_position = (
                position_mapping.get(
                    position_key
                )
            )

            if enum_position is not None:

                values = makeable_tricks.get(
                    enum_position
                )

                if isinstance(
                    values,
                    dict,
                ):

                    return values

        except ImportError:

            pass

        for key, value in makeable_tricks.items():

            if not isinstance(
                value,
                dict,
            ):

                continue

            key_text = str(
                getattr(
                    key,
                    "value",
                    key,
                )
            ).upper()

            if key_text == position_key:

                return value

            if key_text.startswith(
                position_key
            ):

                return value

        return {}

    # =====================================================
    # GET MAKEABLE VALUE
    # =====================================================

    @staticmethod
    def get_makeable_value(
        values,
        denomination,
    ):

        if not isinstance(
            values,
            dict,
        ):

            return None

        value = values.get(
            denomination
        )

        if value is not None:

            return value

        value = values.get(
            denomination.lower()
        )

        if value is not None:

            return value

        try:

            from bidding.bidding_system import Denomination

            denomination_mapping = {
                "C": getattr(
                    Denomination,
                    "CLUBS",
                    None,
                ),
                "D": getattr(
                    Denomination,
                    "DIAMONDS",
                    None,
                ),
                "H": getattr(
                    Denomination,
                    "HEARTS",
                    None,
                ),
                "S": getattr(
                    Denomination,
                    "SPADES",
                    None,
                ),
                "NT": getattr(
                    Denomination,
                    "NT",
                    None,
                ),
            }

            enum_value = (
                denomination_mapping.get(
                    denomination
                )
            )

            if enum_value is not None:

                value = values.get(
                    enum_value
                )

                if value is not None:

                    return value

        except ImportError:

            pass

        for key, value in values.items():

            key_text = str(
                getattr(
                    key,
                    "value",
                    key,
                )
            ).upper()

            key_name = str(
                getattr(
                    key,
                    "name",
                    key,
                )
            ).upper()

            aliases = {
                "C": (
                    "CLUB",
                    "CLUBS",
                    "♣",
                ),
                "D": (
                    "DIAMOND",
                    "DIAMONDS",
                    "♦",
                ),
                "H": (
                    "HEART",
                    "HEARTS",
                    "♥",
                ),
                "S": (
                    "SPADE",
                    "SPADES",
                    "♠",
                ),
                "NT": (
                    "NOTRUMP",
                    "NO_TRUMP",
                    "NO-TRUMP",
                    "NT",
                ),
            }

            if (
                key_text == denomination
                or key_name == denomination
            ):

                return value

            if key_text in aliases.get(
                denomination,
                (),
            ):

                return value

            if key_name in aliases.get(
                denomination,
                (),
            ):

                return value

        return None

    # =====================================================
    # DOUBLING TEXT
    # =====================================================

    @staticmethod
    def get_doubling_text(
        game,
    ):

        doubling_state = getattr(
            game,
            "doubling_state",
            None,
        )

        if doubling_state == SpecialCall.REDOUBLE:

            return "Redoubled"

        if doubling_state == SpecialCall.DOUBLE:

            return "Doubled"

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

        vulnerability = getattr(
            game,
            "vulnerability",
            None,
        )

        if vulnerability is None:

            return "Unknown"

        return str(
            getattr(
                vulnerability,
                "value",
                vulnerability,
            )
        )

    # =====================================================
    # DETERMINE GAME WINNER
    # =====================================================

    @staticmethod
    def get_game_winner(
        game,
    ):

        if not game.is_complete:

            return "Game in progress"

        score = game.final_score

        if score is None:

            score = (
                game.calculate_score()
            )

        if score is None:
            return "Result not available."

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

        while self.tricks_layout.count():

            item = (
                self.tricks_layout.takeAt(
                    0
                )
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

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

            title = QLabel(
                f"TRICK {trick_number}"
            )

            title.setObjectName(
                "trickTitle"
            )

            trick_layout.addWidget(
                title
            )

            cards_layout = QHBoxLayout()

            cards_layout.setSpacing(
                18
            )

            display_order = [
                self.position_from_letter("N"),
                self.position_from_letter("E"),
                self.position_from_letter("S"),
                self.position_from_letter("W"),
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

        self.history_manager.delete_game(
            game_id
        )

        self.selected_game = None

        self.delete_button.setEnabled(
            False
        )

        self.play_deal_button.setEnabled(
            False
        )

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

        self.dealer_label.setText(
            ""
        )

        self.contract_label.setText(
            ""
        )

        self.declarer_label.setText(
            ""
        )

        self.doubling_label.setText(
            ""
        )

        self.vulnerability_label.setText(
            ""
        )

        self.outcome_label.setText(
            ""
        )

        self.game_details.setText(
            "No games have been recorded yet."
        )

        self.notes_edit.clear()

        self.delete_button.setEnabled(
            False
        )

        self.play_deal_button.setEnabled(
            False
        )

        self.makeable_tricks_container.hide()

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

        value = getattr(
            position,
            "value",
            position,
        )

        value_text = str(
            value
        )

        return value_text.title()

    @staticmethod
    def position_letter(
        position,
    ):

        if position is None:

            return "?"

        value = getattr(
            position,
            "value",
            position,
        )

        value_text = str(
            value
        ).upper()

        return value_text

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
            padding-top: 2px;
        }

        QLabel#gameScore {
            color: #e5c557;
            font-size: 15px;
            font-weight: bold;
            padding-bottom: 2px;
        }

        QFrame#gameInfoFrame {
            background-color: #071710;
            border: 1px solid #29483b;
            border-radius: 7px;
        }

        QLabel#gameInfoLabel {
            color: #d1dbd5;
            font-size: 13px;
            padding: 2px 0px;
        }

        QLabel#gameDetails {
            color: #9faea7;
            font-size: 12px;
            padding: 2px 0px 5px 0px;
        }

        QLabel#sectionTitle {
            color: #b9c8c1;
            font-size: 12px;
            letter-spacing: 1px;
        }

        QFrame#makeableTricksContainer {
            background-color: transparent;
        }

        QFrame#makeableTricksTable {
            background-color: #071710;
            border: 1px solid #29483b;
            border-radius: 7px;
        }

        QLabel#makeableHeader {
            color: #e5c557;
            font-size: 13px;
            font-weight: bold;
            padding: 2px;
        }

        QLabel#makeablePosition {
            color: #b9c8c1;
            font-size: 12px;
            font-weight: bold;
            padding: 2px;
        }

        QLabel#makeableValue {
            color: #f1f4f2;
            font-size: 13px;
            font-weight: bold;
            padding: 2px;
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

        QPushButton#playDealButton {
            background-color: #e5c557;
            color: #071710;
            border: none;
            border-radius: 6px;
            padding: 11px 14px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton#playDealButton:hover {
            background-color: #efd477;
        }

        QPushButton#playDealButton:pressed {
            background-color: #c9aa42;
        }

        QPushButton#playDealButton:disabled {
            background-color: #11271d;
            color: #5f6964;
            border: 1px solid #29483b;
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