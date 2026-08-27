from bidding.bid import Bid, Denomination
from bidding.bidding_system import BiddingSystem
from card_model.card import Suit
from card_model.player import Position
from contract.contract import Contract, determine_contract, determine_declarer


def test_passed_out_auction_has_no_contract():
    "all four pass with no bid -> nothing to play"
    system = BiddingSystem(Position.SOUTH)
    system.make_pass(Position.SOUTH)
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    assert determine_contract(system) is None
    assert determine_declarer(system) is None


def test_declarer_is_final_bidder_when_no_partner_bid_first():
    system = BiddingSystem(Position.SOUTH)
    system.make_bid(Position.SOUTH, Bid(1, Denomination.CLUBS))
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    contract = determine_contract(system)

    assert contract.declarer == Position.SOUTH
    assert contract.bid == Bid(1, Denomination.CLUBS)


def test_declarer_is_first_partner_to_name_final_denomination():
    "South opens 1H, North raises to 2H -- South is declarer, not North"
    system = BiddingSystem(Position.SOUTH)
    system.make_bid(Position.SOUTH, Bid(1, Denomination.HEARTS))
    system.make_pass(Position.WEST)
    system.make_bid(Position.NORTH, Bid(2, Denomination.HEARTS))
    system.make_pass(Position.EAST)
    system.make_pass(Position.SOUTH)
    system.make_pass(Position.WEST)

    contract = determine_contract(system)

    assert contract.declarer == Position.SOUTH
    assert contract.bid == Bid(2, Denomination.HEARTS)


def test_declarer_ignores_denomination_named_only_by_opponents():
    "South 1H, West overcalls 1S, North/East pass -- West is declarer"
    system = BiddingSystem(Position.SOUTH)
    system.make_bid(Position.SOUTH, Bid(1, Denomination.HEARTS))
    system.make_bid(Position.WEST, Bid(1, Denomination.SPADES))
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)
    system.make_pass(Position.SOUTH)

    contract = determine_contract(system)

    assert contract.declarer == Position.WEST


def test_trump_suit_matches_denomination():
    system = BiddingSystem(Position.SOUTH)
    system.make_bid(Position.SOUTH, Bid(3, Denomination.SPADES))
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    contract = determine_contract(system)

    assert contract.trump_suit == Suit.SPADES
    assert contract.is_no_trump is False


def test_no_trump_contract_has_no_trump_suit():
    system = BiddingSystem(Position.SOUTH)
    system.make_bid(Position.SOUTH, Bid(1, Denomination.NO_TRUMP))
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    contract = determine_contract(system)

    assert contract.trump_suit is None
    assert contract.is_no_trump is True


def test_dummy_is_declarers_partner():
    system = BiddingSystem(Position.SOUTH)
    system.make_bid(Position.SOUTH, Bid(1, Denomination.CLUBS))
    system.make_pass(Position.WEST)
    system.make_pass(Position.NORTH)
    system.make_pass(Position.EAST)

    contract = determine_contract(system)

    assert contract.declarer == Position.SOUTH
    assert contract.dummy == Position.NORTH


def test_contract_repr_is_human_readable():
    contract = Contract(bid=Bid(4, Denomination.HEARTS), declarer=Position.EAST)

    assert repr(contract) == "4H by E"
