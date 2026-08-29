from game_logic.dealer import determine_next_dealer
from card_model.player import Position


def test_next_dealer_after_south_is_west():
    assert determine_next_dealer(Position.SOUTH) == Position.WEST


def test_next_dealer_after_west_is_north():
    assert determine_next_dealer(Position.WEST) == Position.NORTH


def test_next_dealer_after_north_is_east():
    assert determine_next_dealer(Position.NORTH) == Position.EAST


def test_next_dealer_after_east_is_south():
    assert determine_next_dealer(Position.EAST) == Position.SOUTH