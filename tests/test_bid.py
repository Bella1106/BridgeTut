from bidding.bid import Bid, Denomination
import pytest

def test_denomination_ranking():
    "tests: C < D < H < S < NT"

    assert Denomination.CLUBS < Denomination.DIAMONDS
    assert Denomination.DIAMONDS < Denomination.HEARTS
    assert Denomination.HEARTS < Denomination.SPADES
    assert Denomination.SPADES < Denomination.NO_TRUMP

def test_bid_ranking_within_same_level():
    clubs = Bid(1, Denomination.CLUBS)
    diamonds = Bid(1, Denomination.DIAMONDS)
    hearts = Bid(1, Denomination.HEARTS)
    spades = Bid(1, Denomination.SPADES)
    no_trump = Bid(1, Denomination.NO_TRUMP)

    assert clubs < diamonds
    assert diamonds < hearts
    assert hearts < spades
    assert spades < no_trump

def test_higher_level_outranks_lower_level():
    one_no_trump = Bid(1, Denomination.NO_TRUMP)
    two_clubs = Bid(2, Denomination.CLUBS)

    assert one_no_trump < two_clubs

def test_identical_bids_are_equal():
    first_bid = Bid(3, Denomination.HEARTS)
    second_bid = Bid(3, Denomination.HEARTS)

    assert first_bid == second_bid

def test_different_bids_not_equal():
    hearts = Bid(3, Denomination.HEARTS)
    spades = Bid(3, Denomination.SPADES)

    assert hearts != spades

"illegal object tests"
def test_level_below_one_rejected():
    with pytest.raises(ValueError):
        Bid(0, Denomination.CLUBS)

def test_level_above_seven_rejected():
    with pytest.raises(ValueError):
        Bid(8, Denomination.NO_TRUMP)

def test_invalid_denomination_is_rejected():
    with pytest.raises(TypeError):
        Bid(2, "HEARTS")

def test_boundary_bids_valid():
    lowest_bid = Bid(1, Denomination.CLUBS)
    highest_bid = Bid(7, Denomination.NO_TRUMP)

    assert repr(lowest_bid) == "1C"
    assert repr(highest_bid) == "7NT"