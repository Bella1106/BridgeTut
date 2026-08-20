"""
player.py
---------
Defines a Player (one of the 4 seats at the table) and their Position.

Positions and partnerships, per the rules doc:
    North-South are partners; East-West are partners.
    Seating/play order is always clockwise: South -> West -> North -> East.
"""

from __future__ import annotations
from enum import Enum

from .hand import Hand


class Position(Enum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"

    def __str__(self) -> str:
        return self.value

    @property
    def partner(self) -> "Position":
        return {
            Position.NORTH: Position.SOUTH,
            Position.SOUTH: Position.NORTH,
            Position.EAST: Position.WEST,
            Position.WEST: Position.EAST,
        }[self]

    @property
    def is_north_south(self) -> bool:
        return self in (Position.NORTH, Position.SOUTH)


class Player:
    """One of the 4 people at the table. `name` is optional (useful once
    this is wired up to real user accounts / the tutorial database);
    `position` is required because so much of Bridge's logic (dealer
    rotation, partnerships, declarer) depends on where you're sitting.
    """

    def __init__(self, position: Position, name: str | None = None):
        self.position = position
        self.name = name or position.value
        self.hand = Hand()

    @property
    def partner_position(self) -> Position:
        return self.position.partner

    def __repr__(self) -> str:
        return f"Player({self.name}, {self.position})"
