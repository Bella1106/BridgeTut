"""
Contract Logic package for BridgeTut.

Owned by: Alonso (backlog item 4, "Contract Logic").

Once an auction (BiddingSystem) finishes, this package turns the raw
bidding history into the information the Play phase actually needs:

    contract.py -> Contract, determine_contract(), determine_declarer()

Typical usage:

    from contract.contract import determine_contract

    contract = determine_contract(bidding_system)
    if contract is None:
        ...  # passed out, no play phase
    else:
        contract.trump_suit   # Suit or None (No Trump)
        contract.declarer
        contract.dummy
"""
