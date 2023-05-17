class Player:
    """Abstract base class for all poker-playing agents.

    All agents should inherit from this class and implement the take_action
    method.

    A poker player holds chips to bet with, and has private holecards to play with. 
    The n_chips of contributions to the pot for a given hand of
    poker are stored cumulative, as the total pot to cash out is just the sum
    of all players' contributions. If player is not active, represents folded.
    """

    FOLD = 0
    CALL = 1
    BET = 2
    RAISE = 3
    CHECK = 4
    ACTIONS = [FOLD, BET, CALL, RAISE, CHECK]

    def __init__(self, initial_bigblinds: int):
        """Istantiate a player."""
        self.n_bigblinds = initial_bigblinds
        self.cards = []
        self.is_active = True

    def is_all_in(self) -> bool:
        """Return if the player is all in or not."""
        return self._is_active and self.n_bigblinds == 0

    def take_action(self, board, bets):
        """All poker strategy is implemented here.

        Smart agents have to implement this method to compete. To take an
        action, agents receive the current game state and have to emit the next
        state. Returns one of FOLD, BET, CALL, RAISE, CHECK
        """
        #to-do:
        #if other opponent has bet 0, allowed to check, else not allowed
        #if facing bet, can FOLD, CALL, RAISE
        #if selected action is BET or CALL, must somehow also return amount...

    def __repr__(self):
        return '<n_bigblinds={}, cards={}, folded={}>'.format(
            self.n_bigblinds,
            self.cards,
            not self.is_active)
