"""
Defines the bids that can be made during the bidding phase of Bridge

A contract bid consists of 
    a level from 1 to 7 
    a denominations (clubs, diamons, spades, hearts or NT)

Bids are ranked first by level then by denomination
"""
from enum import IntEnum
from functools import total_ordering

class Denomination(IntEnum):
    "denominations are order by their rank in bidding"
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3
    NO_TRUMP = 4

    @property
    def short(self) -> str:
        return{
            "CLUBS": "C",
            "DIAMONDS" : "D",
            "HEARTS" : "H",
            "SPADES" : "S",
            "NO_TRUMP" : "NT",
        }[self.name]

    def __str__(self) -> str:
        return self.short

@total_ordering
class Bid:
    "represents a contract bid in Bridge"
    def __init__(self, level: int, denomination:Denomination):
        if not 1 <= level <= 7:
            raise ValueError("Bid must be between 1 and 7.")

        if not isinstance(denomination, Denomination):
            raise TypeError('Bid Denomination must be a Denomination.')

        self.level = level
        self.denomination = denomination

    def __repr__(self) -> str:
        return f"{self.level}{self.denomination.short}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Bid):
            return NotImplemented

        return(
            self.level == other.level
            and self.denomination == other.denomination
        )

    def __lt__(self, other: "Bid") -> bool:
        if not isinstance(other, Bid):
            return NotImplemented

        return(self.level, self.denomination) < (other.level, other.denomination)

