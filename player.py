import numpy as np
from evaluator import Evaluator
import strength


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

    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3

    # default starting distribution
    starting_distribution = [1/5] * 8
    
    # Bet size:
    # 0: 1/3 Pot
    # 1: 1/2 Pot
    # 2: 3/4 Pot
    # 3: Pot
    # 4: 1.5 Pot
    # 5: 2 Pot
    # 5: 2.5 Pot
    # 6: 3 Pot
    # 7: 4 Pot

    starting_bet_distribution = [1/8] * 8


    # Raise size:
    # 0: 2/3 Pot
    # 1: 1.5 Pot
    # 2: 2.5 Pot
    # 2: 4 Pot

    starting_raise_distribution = [1/4] * 4

    def __init__(self, initial_bigblinds: int, fold_probability=0.1,
                 raise_probability=0.1, call_probability=0.8):
        """Istantiate a player."""
        self.n_bigblinds = initial_bigblinds
        self.cards = []
        self.is_active = True
        self.fold_probability = fold_probability
        self.raise_probability = raise_probability
        self.call_probability = call_probability
        if not np.isclose(fold_probability+raise_probability+call_probability, 1.0):
            raise ValueError(f'Probabilities passed must sum to one.')

        #initializing the distribution for any possible scenarios

        # Starting Hand breakdown index
        # 0. Best Startings (AA, KK)
        # 1. Second Premiums (AK, QQ)
        # 2. Third Premiums (JJ, 1010, AQ)
        # 3. Two High Cards, 99 88 
        # 4. Remaining Pocket Pairs (77, 66 ...)
        # 5. Rest of the Crowd

        # Best 5 Cards breakdown index
        # 0. Straight Flush
        # 1. Quads
        # 2. Full House
        # 3. Flush
        # 4. Straight
        # 5. Trips
        # 6. Two Pair
        # 7. Pair
        # 8. High Card


        self.inpos_distribution = [[[] for _ in range(9)] for _ in range(4)]
        for i in range(4):
            for j in range(9):
                self.inpos_distribution[i][j] = self.starting_distribution.copy()
        self.opos_distribution = [[[] for _ in range(9)] for _ in range(4)]
        for i in range(4):
            for j in range(9):
                self.opos_distribution[i][j] = self.starting_distribution.copy()
        self.inpos_b_distribution = [[[] for _ in range(9)] for _ in range(4)]
        for i in range(4):
            for j in range(9):
                self.inpos_b_distribution[i][j] = self.starting_bet_distribution.copy()
        self.inpos_r_distribution = [[[] for _ in range(9)] for _ in range(4)]
        for i in range(4):
            for j in range(9):
                self.inpos_r_distribution[i][j] = self.starting_raise_distribution.copy()
        self.opos_b_distribution = [[[] for _ in range(9)] for _ in range(4)]
        for i in range(4):
            for j in range(9):
                self.opos_b_distribution[i][j] = self.starting_bet_distribution.copy()
        self.opos_r_distribution = [[[] for _ in range(9)] for _ in range(4)]
        for i in range(4):
            for j in range(9):
                self.opos_r_distribution[i][j] = self.starting_raise_distribution.copy()
        



    def is_all_in(self) -> bool:
        """Return if the player is all in or not."""
        return self._is_active and self.n_bigblinds == 0

    def take_action(self, board, bets):
        """All poker strategy is implemented here.

        Smart agents have to implement this method to compete. To take an
        action, agents receive the current game state and have to emit the next
        state. Returns one of FOLD, BET, CALL, RAISE, CHECK
        """
        # to-do:
        # if other opponent has bet 0, allowed to check, else not allowed
        # if facing bet, can FOLD, CALL, RAISE
        # if selected action is BET or CALL, must somehow also return amount...
        dice_roll = np.random.sample()
        bound_1 = self.fold_probability
        bound_2 = self.fold_probability + self.raise_probability
        if 0.0 < dice_roll <= bound_1:
            return Player.FOLD
        elif bound_1 < dice_roll <= bound_2:
            return Player.RAISE
        else:
            return Player.CALL

    def __repr__(self):
        return '<n_bigblinds={}, cards={}, folded={}>'.format(
            self.n_bigblinds,
            self.cards,
            not self.is_active)

# a class containing all distributions of a player


