"""
bbo_parser.py
-------------
Parses BBO hand-record HTML files and converts them into the game's
existing Card, Position, Vulnerability and Denomination models.

The BBO examples supplied for the project are HTML documents saved with
a .txt extension, so this parser accepts either raw HTML text or a path
to one of those files.

This parser is intentionally separate from tutorial_parser.py because
BBO records and scripted tutorial lessons have different input formats
and different semantics.

BBO provides:
    - the exact four hands
    - the dealer
    - vulnerability
    - the makeable-tricks table

BBO does NOT provide:
    - a card-by-card correct play script

Therefore BBO games use the normal bidding and play validation logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from bidding.bid import Denomination
from card_model.card import Card, Rank, Suit
from card_model.player import Position
from game_logic.vulnerability import Vulnerability


# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

_POSITION_BY_CLASS = {
    "north": Position.NORTH,
    "south": Position.SOUTH,
    "east": Position.EAST,
    "west": Position.WEST,
}

_POSITION_BY_NAME = {
    "north": Position.NORTH,
    "south": Position.SOUTH,
    "east": Position.EAST,
    "west": Position.WEST,
}

_SUIT_BY_CLASS = {
    "club": Suit.CLUBS,
    "diamond": Suit.DIAMONDS,
    "heart": Suit.HEARTS,
    "spade": Suit.SPADES,
}

_DENOMINATION_BY_SUIT_CLASS = {
    "club": Denomination.CLUBS,
    "diamond": Denomination.DIAMONDS,
    "heart": Denomination.HEARTS,
    "spade": Denomination.SPADES,
}

_RANK_BY_TEXT = {
    "J": Rank.JACK,
    "Q": Rank.QUEEN,
    "K": Rank.KING,
    "A": Rank.ACE,
}

_VULNERABILITY_BY_CODE = {
    "NONE": Vulnerability.NONE,
    "NS": Vulnerability.NORTH_SOUTH,
    "N-S": Vulnerability.NORTH_SOUTH,
    "EW": Vulnerability.EAST_WEST,
    "E-W": Vulnerability.EAST_WEST,
    "BOTH": Vulnerability.BOTH,
}

_TABLE_DENOMINATIONS = (
    Denomination.CLUBS,
    Denomination.DIAMONDS,
    Denomination.HEARTS,
    Denomination.SPADES,
    Denomination.NO_TRUMP,
)


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BBOGameData:
    """
    Stores all information extracted from one BBO hand record.
    """

    hands: dict[Position, list[Card]]
    dealer: Position
    vulnerability: Vulnerability
    makeable_tricks: dict[Position, dict[Denomination, int | None]]


# ---------------------------------------------------------------------------
# HTML parser
# ---------------------------------------------------------------------------

class _BBOHTMLParser(HTMLParser):
    """
    Small stateful parser for the BBO HTML structure.

    The parser deliberately uses Python's standard-library HTMLParser,
    so no additional external dependency is required.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)

        self.depth = 0

        # -------------------------------------------------------------------
        # Hand record state
        # -------------------------------------------------------------------

        self._hand_record_depth: int | None = None
        self._hand_depth: int | None = None

        self._current_position: Position | None = None
        self._current_suit: Suit | None = None

        self._rank_list_depth: int | None = None
        self._rank_item_depth: int | None = None
        self._rank_text: list[str] = []

        self.hands: dict[Position, list[Card]] = {
            position: [] for position in Position
        }

        self.dealer: Position | None = None
        self.vulnerability: Vulnerability | None = None

        # -------------------------------------------------------------------
        # Makeable-tricks table state
        # -------------------------------------------------------------------

        self._table_depth: int | None = None
        self._in_thead = False

        self._table_headers: list[Denomination] = []

        self._current_row: list[str] | None = None
        self._current_cell_text: list[str] = []
        self._in_cell = False

        self.table_rows: list[list[str]] = []

    # -----------------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _attributes(
        attrs: list[tuple[str, str | None]],
    ) -> dict[str, str]:
        return {
            name.lower(): (value or "")
            for name, value in attrs
        }

    @staticmethod
    def _classes(attributes: dict[str, str]) -> set[str]:
        return set(attributes.get("class", "").split())

    # -----------------------------------------------------------------------
    # Start tags
    # -----------------------------------------------------------------------

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self.depth += 1

        attributes = self._attributes(attrs)
        classes = self._classes(attributes)

        # -------------------------------------------------------------------
        # Hand record
        # -------------------------------------------------------------------

        if tag == "div" and "component_hand_record" in classes:
            self._hand_record_depth = self.depth

        elif (
            tag == "div"
            and self._hand_record_depth is not None
            and self._current_position is None
        ):
            position_class = next(
                (
                    class_name
                    for class_name in classes
                    if class_name in _POSITION_BY_CLASS
                ),
                None,
            )

            vulnerability_class = next(
                (
                    class_name
                    for class_name in classes
                    if class_name.startswith("vulnerable-")
                ),
                None,
            )

            # HCP blocks also use .north/.south/.east/.west.
            # The vulnerability class therefore lets us distinguish an
            # actual hand section from an HCP display section.
            if position_class is not None and vulnerability_class is not None:
                self._hand_depth = self.depth
                self._current_position = _POSITION_BY_CLASS[position_class]

                vulnerability_code = (
                    vulnerability_class.split("-", 1)[1].upper()
                )

                try:
                    parsed_vulnerability = _VULNERABILITY_BY_CODE[
                        vulnerability_code
                    ]
                except KeyError as exc:
                    raise ValueError(
                        "Unsupported BBO vulnerability class: "
                        f"{vulnerability_class!r}"
                    ) from exc

                if (
                    self.vulnerability is not None
                    and self.vulnerability is not parsed_vulnerability
                ):
                    raise ValueError(
                        "BBO hand record contains inconsistent "
                        "vulnerability information."
                    )

                self.vulnerability = parsed_vulnerability

        # -------------------------------------------------------------------
        # Suit inside a hand
        # -------------------------------------------------------------------

        if (
            tag == "i"
            and self._current_position is not None
            and self._hand_depth is not None
        ):
            suit_class = next(
                (
                    class_name
                    for class_name in classes
                    if class_name in _SUIT_BY_CLASS
                ),
                None,
            )

            if suit_class is not None:
                self._current_suit = _SUIT_BY_CLASS[suit_class]

        # -------------------------------------------------------------------
        # Rank list inside a suit
        # -------------------------------------------------------------------

        elif (
            tag == "ul"
            and self._current_position is not None
            and self._current_suit is not None
            and self._rank_list_depth is None
        ):
            # The <ul> after the suit icon contains that suit's ranks.
            self._rank_list_depth = self.depth

        # -------------------------------------------------------------------
        # Individual rank
        # -------------------------------------------------------------------

        elif (
            tag == "li"
            and self._rank_list_depth is not None
            and self.depth == self._rank_list_depth + 1
        ):
            self._rank_item_depth = self.depth
            self._rank_text = []

        # -------------------------------------------------------------------
        # Dealer marker
        # -------------------------------------------------------------------

        if (
            tag == "abbr"
            and self._current_position is not None
            and attributes.get("title", "").strip().lower() == "dealer"
        ):
            if (
                self.dealer is not None
                and self.dealer is not self._current_position
            ):
                raise ValueError(
                    "BBO hand record contains more than one dealer."
                )

            self.dealer = self._current_position

        # -------------------------------------------------------------------
        # Makeable-tricks table
        # -------------------------------------------------------------------

        if tag == "table":
            self._table_depth = self.depth
            self._table_headers = []
            self.table_rows = []

        elif tag == "thead" and self._table_depth is not None:
            self._in_thead = True

        elif (
            tag == "i"
            and self._table_depth is not None
            and self._in_thead
        ):
            suit_class = next(
                (
                    class_name
                    for class_name in classes
                    if class_name in _DENOMINATION_BY_SUIT_CLASS
                ),
                None,
            )

            if suit_class is not None:
                self._table_headers.append(
                    _DENOMINATION_BY_SUIT_CLASS[suit_class]
                )

        elif (
            tag in ("th", "td")
            and self._table_depth is not None
        ):
            self._in_cell = True
            self._current_cell_text = []

        elif (
            tag == "tr"
            and self._table_depth is not None
            and not self._in_thead
        ):
            self._current_row = []

    # -----------------------------------------------------------------------
    # Text
    # -----------------------------------------------------------------------

    def handle_data(self, data: str) -> None:
        if (
            self._rank_item_depth is not None
            and self.depth >= self._rank_item_depth
        ):
            self._rank_text.append(data)

        if self._in_cell:
            self._current_cell_text.append(data)

    # -----------------------------------------------------------------------
    # End tags
    # -----------------------------------------------------------------------

    def handle_endtag(self, tag: str) -> None:
        # -------------------------------------------------------------------
        # Individual rank
        # -------------------------------------------------------------------

        if (
            tag == "li"
            and self._rank_item_depth is not None
            and self.depth == self._rank_item_depth
        ):
            rank_text = "".join(self._rank_text).strip().upper()

            if rank_text:
                rank = self._parse_rank(rank_text)

                if (
                    self._current_position is None
                    or self._current_suit is None
                ):
                    raise ValueError(
                        "BBO rank found without a current player and suit."
                    )

                self.hands[self._current_position].append(
                    Card(rank, self._current_suit)
                )

            self._rank_item_depth = None
            self._rank_text = []

        # -------------------------------------------------------------------
        # End of suit rank list
        # -------------------------------------------------------------------

        if (
            tag == "ul"
            and self._rank_list_depth is not None
            and self.depth == self._rank_list_depth
        ):
            self._rank_list_depth = None
            self._current_suit = None

        # -------------------------------------------------------------------
        # Table cells
        # -------------------------------------------------------------------

        if (
            tag in ("th", "td")
            and self._in_cell
        ):
            cell_text = "".join(self._current_cell_text).strip()

            if tag == "th":
                if cell_text.upper() == "NT":
                    self._table_headers.append(
                        Denomination.NO_TRUMP
                    )

            else:
                if self._current_row is None:
                    raise ValueError(
                        "BBO table cell found outside a table row."
                    )

                self._current_row.append(cell_text)

            self._in_cell = False
            self._current_cell_text = []

        # -------------------------------------------------------------------
        # Table row
        # -------------------------------------------------------------------

        elif (
            tag == "tr"
            and self._table_depth is not None
        ):
            if self._current_row is not None:
                self.table_rows.append(self._current_row)

            self._current_row = None

        # -------------------------------------------------------------------
        # Table header
        # -------------------------------------------------------------------

        elif (
            tag == "thead"
            and self._table_depth is not None
        ):
            self._in_thead = False

        # -------------------------------------------------------------------
        # End of table
        # -------------------------------------------------------------------

        elif (
            tag == "table"
            and self._table_depth is not None
        ):
            self._table_depth = None

        # -------------------------------------------------------------------
        # End of a hand
        # -------------------------------------------------------------------

        if (
            tag == "div"
            and self._hand_depth is not None
            and self.depth == self._hand_depth
        ):
            self._hand_depth = None
            self._current_position = None
            self._current_suit = None
            self._rank_list_depth = None
            self._rank_item_depth = None
            self._rank_text = []

        # -------------------------------------------------------------------
        # End of hand record
        # -------------------------------------------------------------------

        if (
            tag == "div"
            and self._hand_record_depth is not None
            and self.depth == self._hand_record_depth
        ):
            self._hand_record_depth = None

        self.depth -= 1

    # -----------------------------------------------------------------------
    # Rank parsing
    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_rank(value: str) -> Rank:
        if value in _RANK_BY_TEXT:
            return _RANK_BY_TEXT[value]

        if value.isdigit():
            numeric_rank = int(value)

            try:
                return Rank(numeric_rank)
            except ValueError as exc:
                raise ValueError(
                    f"Unsupported BBO card rank: {value!r}"
                ) from exc

        raise ValueError(
            f"Unsupported BBO card rank: {value!r}"
        )


# ---------------------------------------------------------------------------
# Position parsing
# ---------------------------------------------------------------------------

def _parse_position(value: str) -> Position:
    normalized = value.strip().lower()

    try:
        return _POSITION_BY_NAME[normalized]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported BBO table position: {value!r}"
        ) from exc


# ---------------------------------------------------------------------------
# Makeable-tricks table
# ---------------------------------------------------------------------------

def _build_makeable_tricks(
    rows: list[list[str]],
    headers: list[Denomination],
) -> dict[Position, dict[Denomination, int | None]]:
    """
    Convert the HTML table rows into:

        {
            Position.NORTH: {
                Denomination.CLUBS: 5,
                Denomination.DIAMONDS: 5,
                ...
            },
            ...
        }
    """

    if headers != list(_TABLE_DENOMINATIONS):
        raise ValueError(
            "Unexpected BBO makeable-tricks table headings. "
            f"Expected {[str(item) for item in _TABLE_DENOMINATIONS]}, "
            f"got {[str(item) for item in headers]}."
        )

    if len(rows) != 4:
        raise ValueError(
            "Expected 4 BBO makeable-tricks rows, "
            f"got {len(rows)}."
        )

    makeable_tricks: dict[
        Position,
        dict[Denomination, int | None],
    ] = {}

    for row in rows:
        if len(row) != 6:
            raise ValueError(
                "Each BBO makeable-tricks row must contain "
                "a player name and 5 values."
            )

        position = _parse_position(row[0])

        if position in makeable_tricks:
            raise ValueError(
                "Duplicate BBO makeable-tricks row for "
                f"{position}."
            )

        values: dict[Denomination, int | None] = {}

        for denomination, raw_value in zip(
            _TABLE_DENOMINATIONS,
            row[1:],
            strict=True,
        ):
            value = raw_value.strip()

            if value == "-":
                values[denomination] = None
                continue

            try:
                numeric_value = int(value)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid BBO makeable-tricks value "
                    f"{value!r} for {position} / {denomination}."
                ) from exc

            if not 0 <= numeric_value <= 13:
                raise ValueError(
                    f"Invalid BBO makeable-tricks count "
                    f"{numeric_value} for "
                    f"{position} / {denomination}."
                )

            values[denomination] = numeric_value

        makeable_tricks[position] = values

    expected_positions = set(Position)

    if set(makeable_tricks) != expected_positions:
        missing = expected_positions - set(makeable_tricks)
        extra = set(makeable_tricks) - expected_positions

        raise ValueError(
            "BBO makeable-tricks table does not contain "
            "exactly one row for each position. "
            f"Missing={missing}, extra={extra}."
        )

    return makeable_tricks


# ---------------------------------------------------------------------------
# Deal validation
# ---------------------------------------------------------------------------

def _validate_deal(
    hands: dict[Position, list[Card]],
) -> None:
    """
    Ensure the parsed hands form one valid 52-card Bridge deal.
    """

    expected_positions = set(Position)

    if set(hands) != expected_positions:
        raise ValueError(
            "BBO deal must contain North, South, East and West."
        )

    all_cards: list[Card] = []

    for position, hand in hands.items():
        if len(hand) != 13:
            raise ValueError(
                f"BBO hand for {position} contains "
                f"{len(hand)} cards; expected 13."
            )

        all_cards.extend(hand)

    if len(all_cards) != 52:
        raise ValueError(
            f"BBO deal contains {len(all_cards)} cards; "
            "expected 52."
        )

    unique_cards = set(all_cards)

    if len(unique_cards) != 52:
        raise ValueError(
            "BBO deal contains duplicate cards."
        )

    expected_cards = {
        Card(rank, suit)
        for suit in Suit
        for rank in Rank
    }

    if unique_cards != expected_cards:
        missing = expected_cards - unique_cards
        extra = unique_cards - expected_cards

        raise ValueError(
            "BBO deal does not contain exactly one copy "
            "of every standard Bridge card. "
            f"Missing={missing}, extra={extra}."
        )


# ---------------------------------------------------------------------------
# Public parser functions
# ---------------------------------------------------------------------------

def parse_bbo_html(html: str) -> BBOGameData:
    """
    Parse one BBO HTML hand record.

    Parameters
    ----------
    html:
        Raw HTML content from a BBO example file.

    Returns
    -------
    BBOGameData
        Parsed hands, dealer, vulnerability and makeable tricks.
    """

    if not isinstance(html, str):
        raise TypeError(
            "BBO HTML must be provided as a string."
        )

    parser = _BBOHTMLParser()

    parser.feed(html)
    parser.close()

    _validate_deal(parser.hands)

    if parser.dealer is None:
        raise ValueError(
            "BBO hand record does not contain a dealer."
        )

    if parser.vulnerability is None:
        raise ValueError(
            "BBO hand record does not contain vulnerability."
        )

    makeable_tricks = _build_makeable_tricks(
        parser.table_rows,
        parser._table_headers,
    )

    return BBOGameData(
        hands={
            position: list(hand)
            for position, hand in parser.hands.items()
        },
        dealer=parser.dealer,
        vulnerability=parser.vulnerability,
        makeable_tricks=makeable_tricks,
    )


def parse_bbo_file(
    path: str | Path,
) -> BBOGameData:
    """
    Read and parse a BBO HTML document saved as a .txt file.
    """

    file_path = Path(path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"BBO file not found: {file_path}"
        )

    html = file_path.read_text(
        encoding="utf-8"
    )

    return parse_bbo_html(html)