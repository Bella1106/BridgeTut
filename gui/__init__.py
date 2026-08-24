"""
GU
Owned by: Nxedile (Sprint 1 backlog item "GUI Interface").

This package contains the desktop application interface for BridgeTut.

The GUI is built using PySide6 and is responsible for displaying
the BridgeTut application and allowing the user to interact with
the game.

Modules:

    main_window.py       -> Main application window and navigation
    home_page.py         -> BridgeTut home screen
    bidding_page.py      -> Bidding screen
    placeholder_page.py  -> Temporary pages for unfinished features

The GUI communicates with the existing BridgeTut backend rather
than implementing the game rules itself.

The backend components include:

    Card
    Hand
    Player
    Deck
    Bid
    BiddingSystem

Typical usage:

    from gui.main_window import MainWindow

    window = MainWindow()
    window.show()
"""