class Player:
    """Abstract base class for all poker-playing agents.

    All agents should inherit from this class and implement the take_action
    method.

    A poker player holds chips to bet with, and has private holecards to play with. 
    The n_chips of contributions to the pot for a given hand of
    poker are stored cumulative, as the total pot to cash out is just the sum
    of all players' contributions. If player is not active, represents folded.
    """

    def __init__(self, initial_bigblinds: int):
        """Istantiate a player."""
        self.n_bigblinds = initial_bigblinds
        self.cards = []
        self._is_active = True

    def __repr__(self):
        return '<n_bigblinds={}, cards={}, folded={}>'.format(
            self.n_bigblinds,
            self.cards,
            not self._is_active)
