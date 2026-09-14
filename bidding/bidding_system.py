"""
Manages the bidding phase of a bridge game.

The bidding system validates calls against the current auction 
and records accepted calls in the bidding history.
"""
from enum import Enum
from bidding.bid import Bid
from card_model.player import Position
from card_model.deck import seating_order_from

class SpecialCall(Enum):
    DOUBLE = "D"
    REDOUBLE = "R"

    def __str__(self):
        return self.value

class BiddingSystem:
    "maintains the state and history of an auction"

    def __init__(self, dealer: Position):
        if not isinstance(dealer, Position):
            raise TypeError("Dealer must be a Position.")

        self.dealer = dealer
        self.turn_order = seating_order_from(dealer)
        self.current_player = dealer
        
        self.history: list[tuple[Position, Bid | SpecialCall | None]] = []
        self.highest_bid: Bid | None = None
        self.doubling_state: SpecialCall | None = None

        self.consecutive_passes = 0
        self.auction_finished = False

    "start helper functions"
    def _advance_turn(self) -> None:
        current_index = self.turn_order.index(self.current_player)
        next_index = (current_index +1 ) % len(self.turn_order)
        self.current_player = self.turn_order[next_index]

    def _is_players_turn(self, player: Position) -> bool:
        return player == self.current_player

    "end helper functions"

    def is_valid_bid(self, bid: Bid) -> bool:
        if self.highest_bid is None:
            return True

        return bid > self.highest_bid

    def make_bid(self, player: Position, bid: Bid) -> bool:
        "attempt to make bid"
        "true -> bid accepted and recorded"
        "false -> bid does not outrank highest bid"

        if not isinstance(player, Position):
            raise TypeError("Player must be a Position")

        if not isinstance(bid, Bid):
            raise TypeError("Bid must be a valid bid")

        if self.auction_finished:
            return False

        if not self._is_players_turn(player):
            return False

        if not self.is_valid_bid(bid):
            return False

        self.history.append((player, bid))
        self.highest_bid = bid
        self.doubling_state = None
        self.consecutive_passes = 0

        self._advance_turn()
        
        return True

    def make_pass(self, player: Position) -> bool:
        if not isinstance(player, Position):
            raise TypeError("Player must be a Position")

        if self.auction_finished:
            return False

        if not self._is_players_turn(player):
            return False

        self.history.append((player, None))
        self.consecutive_passes += 1

        if self.highest_bid is None and self.consecutive_passes == 4:
            self.auction_finished = True
        elif self.highest_bid is not None and self.consecutive_passes == 3:
            self.auction_finished = True
        else:
            self._advance_turn()

        return True

    def highest_bidder(self) -> Position | None:
        for player, call in reversed(self.history):
            if isinstance(call, Bid):
                return player
        return None

    def can_double(self, player: Position) -> bool:
        if not isinstance(player, Position):
            raise TypeError("Player must be a Position")

        if self.auction_finished:
            return False

        if not self._is_players_turn(player):
            return False

        if self.highest_bid is None:
            return False

        if self.doubling_state is not None:
            return False

        highest_bidder = self.highest_bidder()

        if highest_bidder is None:
            return False

        return player.partner != highest_bidder

    def make_double(self, player: Position) -> bool:
        if not self.can_double(player):
            return False

        self.history.append((player, SpecialCall.DOUBLE))
        self.doubling_state = SpecialCall.DOUBLE
        self.consecutive_passes = 0

        self._advance_turn()

        return True

    def can_redouble(self, player: Position) -> bool:
        if not isinstance(player, Position):
            raise TypeError("Player must be a Position")

        if self.auction_finished:
            return False

        if not self._is_players_turn(player):
            return False

        if self.highest_bid is None:
            return False

        if self.doubling_state != SpecialCall.DOUBLE:
            return False

        highest_bidder = self.highest_bidder()

        if highest_bidder is None:
            return False

        return (
            player == highest_bidder
            or player == highest_bidder.partner
        )

    def make_redouble(self, player: Position) -> bool:
        if not self.can_redouble(player):
            return False

        self.history.append((player, SpecialCall.REDOUBLE))
        self.doubling_state = SpecialCall.REDOUBLE
        self.consecutive_passes = 0

        self._advance_turn()

        return True