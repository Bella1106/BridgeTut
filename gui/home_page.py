from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QDialog,
)

from game_logic.tutorial_bbo_examples import get_bbo_tutorials


class HomePage(QWidget):

    def __init__(
        self,
        new_game_callback=None,
        resume_game_callback=None,
        should_show_resume_callback=None,
        history_callback=None,
        tutorials_callback=None,
        lesson_callback=None,
    ):
        super().__init__()

        self.new_game_callback = new_game_callback
        self.resume_game_callback = resume_game_callback
        self.should_show_resume_callback = (
            should_show_resume_callback
        )
        self.history_callback = history_callback
        self.tutorials_callback = tutorials_callback
        self.lesson_callback = lesson_callback

        self.background_overlay = None

        self.setup_ui()

    # =====================================================
    # UI SETUP
    # =====================================================

    def setup_ui(self):

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            32,
            28,
            32,
            32,
        )

        main_layout.setSpacing(25)

        # =================================================
        # GREEN BACKGROUND
        # =================================================

        table = QFrame()
        table.setObjectName("homeTable")

        table_layout = QVBoxLayout(table)

        table_layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        table_layout.setSpacing(30)

        # =================================================
        # TITLE
        # =================================================

        title_container = QWidget()

        title_layout = QVBoxLayout(title_container)

        title_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        title_layout.setSpacing(6)
        title_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("BridgeTut")
        title.setObjectName("homeTitle")

        subtitle = QLabel(
            "Single-player Contract Bridge — "
            "you play North, East, South and West."
        )

        subtitle.setObjectName("homeSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        table_layout.addStretch()
        table_layout.addWidget(title_container)

        # =================================================
        # BUTTON GRID
        # =================================================

        cards = QWidget()

        grid = QGridLayout(cards)

        grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        grid.setSpacing(16)

        # =================================================
        # PLAY
        # =================================================

        play = self.create_home_card(
            "▷",
            "Play",
            "Start a new game or continue an unfinished game.",
            selected=True,
        )

        play.clicked.connect(
            self.show_play_selection
        )

        grid.addWidget(play, 0, 0)

        # =================================================
        # TUTORIALS
        # =================================================

        tutorials = self.create_home_card(
            "✦",
            "Tutorials",
            "Practise guided play, bidding and "
            "BBO example hands.",
        )

        tutorials.clicked.connect(
            self.show_tutorial_selection
        )

        grid.addWidget(tutorials, 0, 1)

        # =================================================
        # GAME HISTORY
        # =================================================

        history = self.create_home_card(
            "↶",
            "Game History",
            "View contracts, results and scores.",
        )

        if self.history_callback:
            history.clicked.connect(
                self.history_callback
            )

        grid.addWidget(history, 1, 0)

        # =================================================
        # EXIT
        # =================================================

        exit_button = self.create_home_card(
            "→",
            "Exit",
            "Close BridgeTut.",
        )

        exit_button.clicked.connect(
            self.close_application
        )

        grid.addWidget(exit_button, 1, 1)

        table_layout.addWidget(cards)
        table_layout.addStretch()

        main_layout.addWidget(table)

        # =================================================
        # STYLES
        # =================================================

        self.setStyleSheet(
            self.get_style()
        )

    # =====================================================
    # BACKGROUND OVERLAY
    # =====================================================

    def show_background_overlay(self):

        if self.background_overlay is not None:
            return

        self.background_overlay = QFrame(self)

        self.background_overlay.setObjectName(
            "backgroundOverlay"
        )

        self.background_overlay.setStyleSheet(
            """
            QFrame#backgroundOverlay {
                background-color: rgba(0, 0, 0, 85);
            }
            """
        )

        self.background_overlay.setGeometry(
            self.rect()
        )

        self.background_overlay.raise_()
        self.background_overlay.show()

    # =====================================================

    def hide_background_overlay(self):

        if self.background_overlay is not None:

            self.background_overlay.hide()
            self.background_overlay.deleteLater()

            self.background_overlay = None

    # =====================================================

    def resizeEvent(self, event):

        super().resizeEvent(event)

        if self.background_overlay is not None:

            self.background_overlay.setGeometry(
                self.rect()
            )

    # =====================================================
    # SHOW DIALOG
    # =====================================================

    def show_dialog(self, dialog):

        self.show_background_overlay()

        try:
            dialog.exec()

        finally:
            self.hide_background_overlay()

    # =====================================================
    # PLAY SELECTION
    # =====================================================

    def show_play_selection(self):

        # -------------------------------------------------
        # If there is no unfinished game, go straight to
        # a new game.
        #
        # This means the Play card does not unnecessarily
        # show a Resume/New Game popup after a completed
        # game or when there is no saved game.
        # -------------------------------------------------

        has_unfinished_game = False

        if self.should_show_resume_callback:

            has_unfinished_game = (
                self.should_show_resume_callback()
            )

        if not has_unfinished_game:

            if self.new_game_callback:

                self.new_game_callback()

            return

        # =================================================
        # THERE IS AN UNFINISHED GAME
        # =================================================

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Play"
        )

        dialog.setModal(True)

        dialog.setMinimumWidth(
            520
        )

        dialog.setStyleSheet(
            self.get_dialog_style()
        )

        layout = QVBoxLayout(
            dialog
        )

        layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        layout.setSpacing(
            12
        )

        # =================================================
        # TITLE
        # =================================================

        title = QLabel(
            "PLAY"
        )

        title.setObjectName(
            "tutorialTitle"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title
        )

        # =================================================
        # SUBTITLE
        # =================================================

        subtitle = QLabel(
            "You have an unfinished game."
        )

        subtitle.setObjectName(
            "tutorialSubtitle"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            8
        )

        # =================================================
        # NEW GAME
        # =================================================

        new_game = self.create_tutorial_option(
            "1",
            "New Game",
            "Start a completely new Bridge game. "
            "Your unfinished game will remain in history.",
        )

        new_game.clicked.connect(
            lambda: self.start_new_game(
                dialog
            )
        )

        layout.addWidget(
            new_game
        )

        # =================================================
        # RESUME GAME
        # =================================================

        resume_game = self.create_tutorial_option(
            "2",
            "Resume Game",
            "Continue your unfinished game "
            "from where you left off.",
        )

        if self.resume_game_callback:

            resume_game.clicked.connect(
                lambda: self.resume_game(
                    dialog
                )
            )

        else:

            resume_game.setEnabled(
                False
            )

        layout.addWidget(
            resume_game
        )

        # =================================================
        # CANCEL
        # =================================================

        cancel = QPushButton(
            "CANCEL"
        )

        cancel.setObjectName(
            "cancelButton"
        )

        cancel.setCursor(
            Qt.PointingHandCursor
        )

        cancel.clicked.connect(
            dialog.reject
        )

        layout.addSpacing(
            6
        )

        layout.addWidget(
            cancel,
            alignment=Qt.AlignRight,
        )

        self.show_dialog(dialog)

    # =====================================================
    # START NEW GAME
    # =====================================================

    def start_new_game(
        self,
        dialog,
    ):

        dialog.accept()

        if self.new_game_callback:

            self.new_game_callback()

    # =====================================================
    # RESUME GAME
    # =====================================================

    def resume_game(
        self,
        dialog,
    ):

        dialog.accept()

        if self.resume_game_callback:

            self.resume_game_callback()

    # =====================================================
    # TUTORIAL SELECTION
    # =====================================================

    def show_tutorial_selection(self):

        dialog = QDialog(self)

        dialog.setWindowTitle(
            "Tutorials"
        )

        dialog.setModal(
            True
        )

        dialog.setMinimumWidth(
            520
        )

        dialog.setStyleSheet(
            self.get_dialog_style()
        )

        layout = QVBoxLayout(
            dialog
        )

        layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        layout.setSpacing(
            12
        )

        # =================================================
        # TITLE
        # =================================================

        title = QLabel(
            "TUTORIALS"
        )

        title.setObjectName(
            "tutorialTitle"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title
        )

        # =================================================
        # SUBTITLE
        # =================================================

        subtitle = QLabel(
            "Choose how you would like to practise."
        )

        subtitle.setObjectName(
            "tutorialSubtitle"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            8
        )

        # =================================================
        # 1. PLAY ONLY
        # =================================================

        play_only = self.create_tutorial_option(
            "1",
            "Play Only",
            "Practise card play using a fixed lesson.",
        )

        play_only.clicked.connect(
            lambda: self.start_play_only(dialog)
        )

        layout.addWidget(
            play_only
        )

        # =================================================
        # 2. BID + PLAY
        # =================================================

        bid_and_play = self.create_tutorial_option(
            "2",
            "Bid + Play",
            "Practise guided bidding followed by "
            "the prescribed card play.",
        )

        bid_and_play.clicked.connect(
            lambda: self.start_bid_and_play(dialog)
        )

        layout.addWidget(
            bid_and_play
        )

        # =================================================
        # 3. BBO EXAMPLES
        # =================================================

        bbo = self.create_tutorial_option(
            "3",
            "BBO Examples",
            "Play fixed BBO example hands.",
        )

        bbo.clicked.connect(
            lambda: self.start_bbo(dialog)
        )

        layout.addWidget(
            bbo
        )

        # =================================================
        # CANCEL
        # =================================================

        cancel = QPushButton(
            "CANCEL"
        )

        cancel.setObjectName(
            "cancelButton"
        )

        cancel.setCursor(
            Qt.PointingHandCursor
        )

        cancel.clicked.connect(
            dialog.reject
        )

        layout.addSpacing(
            6
        )

        layout.addWidget(
            cancel,
            alignment=Qt.AlignRight,
        )

        self.show_dialog(dialog)

    # =====================================================
    # PLAY ONLY
    # =====================================================

    def start_play_only(
        self,
        dialog,
    ):

        dialog.accept()

        if self.lesson_callback:

            self.lesson_callback(
                "play_only"
            )

        elif self.tutorials_callback:

            self.tutorials_callback(
                "tutorial",
                "examplePlayOnly.txt",
            )

    # =====================================================
    # BID + PLAY
    # =====================================================

    def start_bid_and_play(
        self,
        dialog,
    ):

        dialog.accept()

        if self.lesson_callback:

            self.lesson_callback(
                "bid_and_play"
            )

        elif self.tutorials_callback:

            self.tutorials_callback(
                "tutorial",
                "exampleBidAndPlay.txt",
            )

    # =====================================================
    # BBO
    # =====================================================

    def start_bbo(
        self,
        dialog,
    ):

        dialog.accept()

        bbo_tutorials = get_bbo_tutorials()

        bbo_dialog = QDialog(
            self
        )

        bbo_dialog.setWindowTitle(
            "BBO Examples"
        )

        bbo_dialog.setModal(
            True
        )

        bbo_dialog.setMinimumWidth(
            520
        )

        bbo_dialog.setStyleSheet(
            self.get_dialog_style()
        )

        layout = QVBoxLayout(
            bbo_dialog
        )

        layout.setContentsMargins(
            28,
            24,
            28,
            24,
        )

        layout.setSpacing(
            12
        )

        # =================================================
        # TITLE
        # =================================================

        title = QLabel(
            "BBO EXAMPLES"
        )

        title.setObjectName(
            "tutorialTitle"
        )

        title.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title
        )

        # =================================================
        # SUBTITLE
        # =================================================

        subtitle = QLabel(
            "Choose a BBO example hand to practise."
        )

        subtitle.setObjectName(
            "tutorialSubtitle"
        )

        subtitle.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            8
        )

        # =================================================
        # BBO EXAMPLES
        # =================================================

        for number, tutorial in enumerate(
            bbo_tutorials,
            start=1,
        ):

            option = self.create_tutorial_option(
                str(number),
                tutorial.name,
                "Play this fixed BBO example hand.",
            )

            option.clicked.connect(
                lambda checked=False,
                tutorial=tutorial:
                    self.load_bbo_tutorial(
                        bbo_dialog,
                        tutorial,
                    )
            )

            layout.addWidget(
                option
            )

        # =================================================
        # CANCEL
        # =================================================

        cancel = QPushButton(
            "CANCEL"
        )

        cancel.setObjectName(
            "cancelButton"
        )

        cancel.setCursor(
            Qt.PointingHandCursor
        )

        cancel.clicked.connect(
            bbo_dialog.reject
        )

        layout.addSpacing(
            6
        )

        layout.addWidget(
            cancel,
            alignment=Qt.AlignRight,
        )

        self.show_dialog(bbo_dialog)

    # =====================================================
    # LOAD BBO TUTORIAL
    # =====================================================

    def load_bbo_tutorial(
        self,
        dialog,
        tutorial,
    ):

        dialog.accept()

        if self.tutorials_callback:

            self.tutorials_callback(
                "bbo",
                tutorial.filename,
            )

    # =====================================================
    # CREATE TUTORIAL OPTION
    # =====================================================

    @staticmethod
    def create_tutorial_option(
        icon,
        title,
        description,
    ):

        button = QPushButton()

        button.setObjectName(
            "tutorialOption"
        )

        button.setMinimumHeight(
            78
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        layout = QHBoxLayout(
            button
        )

        layout.setContentsMargins(
            15,
            10,
            15,
            10,
        )

        layout.setSpacing(
            15
        )

        # -------------------------------------------------
        # ICON
        # -------------------------------------------------

        icon_label = QLabel(
            icon
        )

        icon_label.setObjectName(
            "tutorialIcon"
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setFixedWidth(
            40
        )

        layout.addWidget(
            icon_label
        )

        # -------------------------------------------------
        # TEXT
        # -------------------------------------------------

        text_container = QWidget()

        text_layout = QVBoxLayout(
            text_container
        )

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            2
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "tutorialOptionTitle"
        )

        description_label = QLabel(
            description
        )

        description_label.setObjectName(
            "tutorialOptionDescription"
        )

        description_label.setWordWrap(
            True
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            description_label
        )

        layout.addWidget(
            text_container
        )

        return button

    # =====================================================
    # CREATE HOME CARD
    # =====================================================

    @staticmethod
    def create_home_card(
        icon,
        title,
        description,
        selected=False,
    ):

        button = QPushButton()

        button.setObjectName(
            "homeCard"
        )

        button.setProperty(
            "selected",
            selected,
        )

        button.setMinimumHeight(
            92
        )

        button.setCursor(
            Qt.PointingHandCursor
        )

        layout = QHBoxLayout(
            button
        )

        layout.setContentsMargins(
            15,
            12,
            15,
            12,
        )

        layout.setSpacing(
            15
        )

        icon_label = QLabel(
            icon
        )

        icon_label.setObjectName(
            "homeIcon"
        )

        icon_label.setAlignment(
            Qt.AlignCenter
        )

        icon_label.setFixedWidth(
            35
        )

        layout.addWidget(
            icon_label
        )

        text_container = QWidget()

        text_layout = QVBoxLayout(
            text_container
        )

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            3
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "homeCardTitle"
        )

        description_label = QLabel(
            description
        )

        description_label.setObjectName(
            "homeCardDescription"
        )

        description_label.setWordWrap(
            True
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            description_label
        )

        layout.addWidget(
            text_container
        )

        return button

    # =====================================================
    # DIALOG STYLE
    # =====================================================

    @staticmethod
    def get_dialog_style():

        return """

        QDialog {
            background-color: #00602e;
        }

        QLabel#tutorialTitle {
            color: #e5c557;
            font-family: Georgia, serif;
            font-size: 28px;
            font-weight: bold;
        }

        QLabel#tutorialSubtitle {
            color: #d9ebe3;
            font-size: 14px;
        }

        QPushButton#tutorialOption {
            background-color: #11271d;
            border: 1px solid #29483b;
            border-radius: 8px;
            color: #f1f4f2;
            text-align: left;
        }

        QPushButton#tutorialOption:hover {
            background-color: #18382a;
            border: 1px solid #e5c557;
        }

        QPushButton#tutorialOption:pressed {
            background-color: #0d2118;
        }

        QPushButton#tutorialOption:disabled {
            background-color: #172c23;
            border: 1px solid #263d33;
            color: #596860;
        }

        QLabel#tutorialIcon {
            color: #e5c557;
            font-size: 24px;
            font-weight: bold;
        }

        QLabel#tutorialOptionTitle {
            color: #f1f4f2;
            font-size: 16px;
            font-weight: bold;
        }

        QLabel#tutorialOptionDescription {
            color: #aebbb5;
            font-size: 12px;
        }

        QPushButton#cancelButton {
            background-color: #172c23;
            border: 1px solid #29483b;
            border-radius: 6px;
            color: #c6d0cb;
            padding: 9px 18px;
            font-size: 13px;
            font-weight: bold;
        }

        QPushButton#cancelButton:hover {
            background-color: #18382a;
            color: #f1f4f2;
        }

        """

    # =====================================================
    # HOME STYLE
    # =====================================================

    @staticmethod
    def get_style():

        return """

        QWidget {
            font-family: "Segoe UI", Arial, sans-serif;
        }

        QFrame#homeTable {
            background-color: #00602e;
            border-radius: 12px;
        }

        QLabel#homeTitle {
            color: #e5c557;
            font-family: Georgia, serif;
            font-size: 44px;
            font-weight: bold;
        }

        QLabel#homeSubtitle {
            color: #d9ebe3;
            font-size: 17px;
            padding-top: 4px;
        }

        QPushButton#homeCard {
            background-color: #11271d;
            border: 1px solid #29483b;
            border-radius: 10px;
            color: #f1f4f2;
            text-align: left;
            padding: 18px;
        }

        QPushButton#homeCard:hover {
            background-color: #18382a;
            border: 1px solid #e5c557;
        }

        QPushButton#homeCard[selected="true"] {
            background-color: #18382a;
            border: 2px solid #e5c557;
        }

        QPushButton#homeCard:pressed {
            background-color: #0d2118;
        }

        QLabel#homeIcon {
            color: #e5c557;
            font-size: 28px;
        }

        QLabel#homeCardTitle {
            color: #f1f4f2;
            font-size: 18px;
            font-weight: bold;
        }

        QLabel#homeCardDescription {
            color: #aebbb5;
            font-size: 13px;
        }

        """

    # =====================================================
    # EXIT
    # =====================================================

    def close_application(self):

        QApplication.quit()