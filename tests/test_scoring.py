""" 
test_scoring.py 
--------------- 
Unit tests for BridgeTut scoring. 
 
These tests cover: 
 
- Undoubled contracts 
- Doubled contracts 
- Redoubled contracts 
- Made contracts 
- Failed contracts 
- Vulnerable and non-vulnerable scoring 
- North-South / East-West perspective 
- Backwards compatibility with doubled=True 
""" 
 
import pytest 
from types import SimpleNamespace 
 
from bidding.bid import Denomination 
from bidding.bidding_system import SpecialCall 
from card_model.player import Position 
from game_logic.scoring import calculate_score 
 
 
def make_contract( 
    level, 
    denomination, 
    declarer, 
): 
    """Create the minimum Contract-like object needed by scoring.py.""" 
 
    return SimpleNamespace( 
        level=level, 
        denomination=denomination, 
        declarer=declarer, 
    ) 
 
 
# ===================================================== 
# UNDoubled contracts MADE 
# ===================================================== 
 
def test_undoubled_1d_vulnerable_made_exactly(): 
 
    contract = make_contract( 
        1, 
        Denomination.DIAMONDS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=7, 
        vulnerable=True, 
    ) 
 
    assert score == 70 
 
 
def test_undoubled_2h_vulnerable_made_exactly(): 
 
    contract = make_contract( 
        2, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=8, 
        vulnerable=True, 
    ) 
 
    assert score == 110 
 
 
def test_undoubled_4c_non_vulnerable_with_overtricks(): 
 
    contract = make_contract( 
        4, 
        Denomination.CLUBS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=10, 
        vulnerable=False, 
    ) 
 
    assert score == 130 
 
 
def test_undoubled_1nt_non_vulnerable_made_exactly(): 
 
    contract = make_contract( 
        1, 
        Denomination.NO_TRUMP, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=7, 
        vulnerable=False, 
    ) 
 
    assert score == 90 
 
 
# ===================================================== 
# DOUBLED contracts MADE 
# ===================================================== 
 
def test_doubled_part_score_non_vulnerable_made(): 
 
    contract = make_contract( 
        1, 
        Denomination.DIAMONDS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=7, 
        vulnerable=False, 
        doubling_state=SpecialCall.DOUBLE, 
    ) 
 
    assert score == 140 
 
 
def test_doubled_game_vulnerable_made(): 
 
    contract = make_contract( 
        4, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=10, 
        vulnerable=True, 
        doubling_state=SpecialCall.DOUBLE, 
    ) 
 
    assert score == 790 
 
 
# ===================================================== 
# REDOUBLED contracts MADE 
# ===================================================== 
 
def test_redoubled_part_score_non_vulnerable_made(): 
 
    contract = make_contract( 
        1, 
        Denomination.DIAMONDS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=7, 
        vulnerable=False, 
        doubling_state=SpecialCall.REDOUBLE, 
    ) 
 
    assert score == 230 
 
 
def test_redoubled_game_vulnerable_made(): 
 
    contract = make_contract( 
        4, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=10, 
        vulnerable=True, 
        doubling_state=SpecialCall.REDOUBLE, 
    ) 
 
    assert score == 1080 
 
 
# ===================================================== 
# UNDoubled contracts FAILED 
# ===================================================== 
 
def test_undoubled_failed_non_vulnerable(): 
 
    contract = make_contract( 
        2, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=6, 
        vulnerable=False, 
    ) 
 
    assert score == -100 
 
 
def test_undoubled_failed_vulnerable(): 
 
    contract = make_contract( 
        2, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=6, 
        vulnerable=True, 
    ) 
 
    assert score == -200 
 
 
# ===================================================== 
# DOUBLED contracts FAILED 
# ===================================================== 
 
def test_doubled_failed_non_vulnerable_one_down(): 
 
    contract = make_contract( 
        2, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=7, 
        vulnerable=False, 
        doubling_state=SpecialCall.DOUBLE, 
    ) 
 
    assert score == -100 
 
 
def test_doubled_failed_non_vulnerable_three_down(): 
 
    contract = make_contract( 
        4, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=7, 
        vulnerable=False, 
        doubling_state=SpecialCall.DOUBLE, 
    ) 
 
    assert score == -500 
 
 
def test_doubled_failed_non_vulnerable_four_down(): 
 
    contract = make_contract( 
        4, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=6, 
        vulnerable=False, 
        doubling_state=SpecialCall.DOUBLE, 
    ) 
 
    # BridgeTut scoring spreadsheet: 
    # 4 undertricks non-vulnerable when doubled = 800. 
    assert score == -800 
 
 
def test_doubled_failed_vulnerable_four_down(): 
 
    contract = make_contract( 
        4, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=6, 
        vulnerable=True, 
        doubling_state=SpecialCall.DOUBLE, 
    ) 
 
    assert score == -1100 
 
 
# ===================================================== 
# REDOUBLED contracts FAILED 
# ===================================================== 
 
def test_redoubled_failed_non_vulnerable_three_down(): 
 
    contract = make_contract( 
        4, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=7, 
        vulnerable=False, 
        doubling_state=SpecialCall.REDOUBLE, 
    ) 
 
    assert score == -1000 
 
 
def test_redoubled_failed_vulnerable_four_down(): 
 
    contract = make_contract( 
        4, 
        Denomination.HEARTS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=6, 
        vulnerable=True, 
        doubling_state=SpecialCall.REDOUBLE, 
    ) 
 
    assert score == -2200 
 
 
# ===================================================== 
# NORTH-SOUTH PERSPECTIVE 
# ===================================================== 
 
def test_east_west_declarer_reverses_made_score(): 
 
    contract = make_contract( 
        1, 
        Denomination.DIAMONDS, 
        Position.EAST, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.EAST, 
        tricks_made=7, 
        vulnerable=False, 
    ) 
 
    assert score == -70 
 
 
def test_east_west_declarer_reverses_failed_score(): 
 
    contract = make_contract( 
        2, 
        Denomination.HEARTS, 
        Position.WEST, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.WEST, 
        tricks_made=6, 
        vulnerable=False, 
        doubling_state=SpecialCall.DOUBLE, 
    ) 
 
    assert score == 300 
 
 
# ===================================================== 
# BACKWARDS COMPATIBILITY 
# ===================================================== 
 
def test_doubled_boolean_still_works(): 
 
    contract = make_contract( 
        1, 
        Denomination.DIAMONDS, 
        Position.NORTH, 
    ) 
 
    score = calculate_score( 
        contract=contract, 
        declarer=Position.NORTH, 
        tricks_made=7, 
        vulnerable=False, 
        doubled=True, 
    ) 
 
    assert score == 140 
 
 
# ===================================================== 
# EDGE CASES 
# ===================================================== 
 
def test_none_contract_returns_zero(): 
 
    score = calculate_score( 
        contract=None, 
        declarer=Position.NORTH, 
        tricks_made=13, 
        vulnerable=False, 
    ) 
 
    assert score == 0 