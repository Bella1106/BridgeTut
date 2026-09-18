"""
BBO tutorial examples for BridgeTut.

This module defines the BBO examples that are available as tutorials.
It does not parse the BBO files itself; parsing is handled by
game_logic.bbo_parser.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from game_logic.bbo_parser import BBOGameData, parse_bbo_file


@dataclass(frozen=True)
class BBOTutorial:
    """A BBO example that can be loaded as a BridgeTut tutorial."""

    name: str
    filename: str


BBO_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "bbo"
)


BBO_TUTORIALS = (
    BBOTutorial(
        name="Game 20",
        filename="25-07-2026-game20.txt",
    ),
    BBOTutorial(
        name="Hand 16",
        filename="260725-hand16.txt",
    ),
)


def get_bbo_tutorials() -> tuple[BBOTutorial, ...]:
    """Return all available BBO tutorials."""
    return BBO_TUTORIALS


def get_bbo_tutorial_path(tutorial: BBOTutorial) -> Path:
    """Return the file path for a BBO tutorial."""
    return BBO_DIRECTORY / tutorial.filename


def load_bbo_tutorial(tutorial: BBOTutorial) -> BBOGameData:
    """Load and parse a BBO tutorial example."""
    return parse_bbo_file(get_bbo_tutorial_path(tutorial))