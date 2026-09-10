"""
scoring.py
----------
Calculates the score for a completed BridgeTut contract.

Scoring follows the BridgeTut scoring spreadsheet.

The returned score is always from the North-South perspective:

    Positive score -> North-South gain points
    Negative score -> East-West gain points

Redoubles are not supported.
"""

from bidding.bid import Denomination
from card_model.player import Position


def calculate_score(
    contract,
    declarer,
    tricks_made,
    vulnerable,
    doubled=False,
):
    """
    Calculate the score for a completed contract.

    Parameters
    ----------
    contract : Contract
        The final contract.

    declarer : Position
        Player who is declarer.

    tricks_made : int
        Number of tricks won by the declaring partnership.

    vulnerable : bool
        Whether the declaring partnership is vulnerable.

    doubled : bool
        Whether the contract was doubled.

    Returns
    -------
    int
        Score from the North-South perspective.
    """

    if contract is None:
        return 0

    level = contract.level

    denomination = contract.denomination

    required_tricks = level + 6

    # =====================================================
    # DECLARING PARTNERSHIP
    # =====================================================

    declarer_is_ns = declarer in (
        Position.NORTH,
        Position.SOUTH,
    )

    # =====================================================
    # CONTRACT MADE
    # =====================================================

    if tricks_made >= required_tricks:

        overtricks = (
            tricks_made
            - required_tricks
        )

        if doubled:

            score = _doubled_made_score(
                level=level,
                denomination=denomination,
                overtricks=overtricks,
                vulnerable=vulnerable,
            )

        else:

            score = _undoubled_made_score(
                level=level,
                denomination=denomination,
                overtricks=overtricks,
                vulnerable=vulnerable,
            )

    # =====================================================
    # CONTRACT FAILED
    # =====================================================

    else:

        undertricks = (
            required_tricks
            - tricks_made
        )

        if doubled:

            score = -_doubled_penalty(
                undertricks=undertricks,
                vulnerable=vulnerable,
            )

        else:

            score = -_undoubled_penalty(
                undertricks=undertricks,
                vulnerable=vulnerable,
            )

    # =====================================================
    # NORTH-SOUTH PERSPECTIVE
    # =====================================================

    if not declarer_is_ns:

        score = -score

    return score


# =========================================================
# UNDOUBLED CONTRACT MADE
# =========================================================

def _undoubled_made_score(
    level,
    denomination,
    overtricks,
    vulnerable,
):
    """
    Calculate an undoubled contract that was made.
    """

    trick_score = _trick_score(
        level,
        denomination,
    )

    overtrick_value = _overtrick_value(
        denomination,
    )

    # =====================================================
    # GRAND SLAM
    # =====================================================

    if level == 7:

        if vulnerable:
            return 2220

        return 1520

    # =====================================================
    # SLAM
    # =====================================================

    if level == 6:

        bonus = (
            750
            if vulnerable
            else 500
        )

        return (
            trick_score
            + bonus
            + (
                overtricks
                * overtrick_value
            )
        )

    # =====================================================
    # GAME
    # =====================================================

    if _is_game_contract(
        level,
        denomination,
    ):

        bonus = (
            500
            if vulnerable
            else 300
        )

        return (
            trick_score
            + bonus
            + (
                overtricks
                * overtrick_value
            )
        )

    # =====================================================
    # PART SCORE
    # =====================================================

    return (
        trick_score
        + 50
        + (
            overtricks
            * overtrick_value
        )
    )


# =========================================================
# DOUBLED CONTRACT MADE
# =========================================================

def _doubled_made_score(
    level,
    denomination,
    overtricks,
    vulnerable,
):
    """
    Calculate a doubled contract that was made.

    Includes:

    - doubled trick score
    - 50 point insult bonus
    - game/slam bonus
    - doubled overtricks
    """

    trick_score = _trick_score(
        level,
        denomination,
    )

    overtrick_value = (
        200
        if vulnerable
        else 100
    )

    score = (
        trick_score * 2
    ) + 50

    # =====================================================
    # GRAND SLAM
    # =====================================================

    if level == 7:

        if vulnerable:
            score += 1500

        else:
            score += 1000

    # =====================================================
    # SLAM
    # =====================================================

    elif level == 6:

        bonus = (
            750
            if vulnerable
            else 500
        )

        score += bonus

    # =====================================================
    # GAME
    # =====================================================

    elif _is_game_contract(
        level,
        denomination,
    ):

        bonus = (
            500
            if vulnerable
            else 300
        )

        score += bonus

    # =====================================================
    # PART SCORE
    # =====================================================

    else:

        score += 50

    score += (
        overtricks
        * overtrick_value
    )

    return score


# =========================================================
# UNDOUBLED CONTRACT FAILED
# =========================================================

def _undoubled_penalty(
    undertricks,
    vulnerable,
):
    """
    Calculate the penalty for an undoubled failed contract.
    """

    if vulnerable:

        return undertricks * 100

    return undertricks * 50


# =========================================================
# DOUBLED CONTRACT FAILED
# =========================================================

def _doubled_penalty(
    undertricks,
    vulnerable,
):
    """
    Calculate the penalty for a doubled failed contract.

    Vulnerable:
        1 undertrick = 200
        each additional = 300

    Not vulnerable:
        1 undertrick = 100
        2 undertricks = 300
        3+ undertricks = +200 each
    """

    if undertricks <= 0:

        return 0

    if vulnerable:

        return (
            200
            + (
                (undertricks - 1)
                * 300
            )
        )

    if undertricks == 1:

        return 100

    if undertricks == 2:

        return 300

    return (
        300
        + (
            (undertricks - 2)
            * 200
        )
    )


# =========================================================
# TRICK SCORE
# =========================================================

def _trick_score(
    level,
    denomination,
):
    """
    Calculate the score for contracted tricks.
    """

    if denomination in (
        Denomination.CLUBS,
        Denomination.DIAMONDS,
    ):

        return 20 * level

    if denomination in (
        Denomination.HEARTS,
        Denomination.SPADES,
    ):

        return 30 * level

    if denomination == Denomination.NO_TRUMP:

        return (
            40
            + (
                30
                * (level - 1)
            )
        )

    return 0


# =========================================================
# OVERTRICK VALUE
# =========================================================

def _overtrick_value(
    denomination,
):
    """
    Return the value of an undoubled overtrick.
    """

    if denomination in (
        Denomination.CLUBS,
        Denomination.DIAMONDS,
    ):

        return 20

    if denomination in (
        Denomination.HEARTS,
        Denomination.SPADES,
        Denomination.NO_TRUMP,
    ):

        return 30

    return 0


# =========================================================
# GAME DETECTION
# =========================================================

def _is_game_contract(
    level,
    denomination,
):
    """
    Determine whether a contract qualifies as game.

    Game contracts:

        3NT
        4H
        4S
        5C
        5D
    """

    if (
        level == 3
        and denomination == Denomination.NO_TRUMP
    ):

        return True

    if (
        level == 4
        and denomination in (
            Denomination.HEARTS,
            Denomination.SPADES,
        )
    ):

        return True

    if (
        level == 5
        and denomination in (
            Denomination.CLUBS,
            Denomination.DIAMONDS,
        )
    ):

        return True

    return False