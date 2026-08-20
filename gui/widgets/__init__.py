"""
Reusable GUI widgets for BridgeTut.

This package contains reusable PySide6 components used to build
the BridgeTut desktop interface.

Modules:

    card_widget.py  -> Displays an individual Bridge card
    player_seat.py  -> Displays a player's position and hand

These widgets are designed to keep the GUI modular and reusable.
For example, the same PlayerSeat widget can be used for North,
South, East, and West.

Typical usage:

    from gui.widgets.card_widget import CardWidget
    from gui.widgets.player_seat import PlayerSeat

    card_widget = CardWidget(card)
    player_seat = PlayerSeat(player)
"""