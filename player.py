import numpy as np
from evaluator import Evaluator
import strength
import random

class Player:
    """Abstract base class for all poker-playing agents.

    All agents should inherit from this class and implement the take_action
    method.

    A poker player holds chips to bet with, and has private holecards to play with. 
    The n_chips of contributions to the pot for a given hand of
    poker are stored cumulative, as the total pot to cash out is just the sum
    of all players' contributions. If player is not active, represents folded.
    """

    # FOLD = 0
    # CALL = 1
    # BET = 2
    # RAISE = 3
    # CHECK = 4
    # ACTIONS = [FOLD, BET, CALL, RAISE, CHECK]

    FOLD = 0
    CALL = 1
    BET_1 = 2
    BET_2 = 3
    BET_3 = 4
    BET_4 = 5
    BET_5 = 6
    BET_6 = 7
    RAISE_1 = 10
    RAISE_2 = 11
    RAISE_3 = 12
    RAISE_4 = 13
    CHECK = 14

    ACTIONS = [FOLD, CALL, BET_1, BET_2, BET_3, BET_4, BET_5, BET_6, RAISE_1, RAISE_2, RAISE_3, RAISE_4, CHECK]

    bet_arr = [1/3, 1/2, 2/3, 1, 1.5, 2]

    bet_dt = {BET_1 : 1/3, BET_2 : 1/2, BET_3 : 2/3, BET_4: 1, BET_5 : 1.5, BET_6 : 2}

    raise_arr = [2/3, 1.5, 2.5, 4]

    raise_dt = {RAISE_1 : 2/3, RAISE_2 : 1.5, RAISE_3 : 2.5, RAISE_4 : 4}


    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3

    # default starting distribution
    starting_distribution = [1/ len(ACTIONS)] * len(ACTIONS)
    
    # Bet size:
    # 0: 1/3 Pot
    # 1: 1/2 Pot
    # 2: 2/3 Pot
    # 3: Pot
    # 4: 1.5 Pot
    # 5: 2 Pot
    # 6: 3 Pot
    # 7: 4 Pot

    BET_SIZE = [1/3, 1/2, 3/4, 1, 1.5, 2, 2.5, 3, 4]
    starting_bet_distribution = [1/8] * 8


    # Raise size:
    # 0: 2/3 Pot
    # 1: 1.5 Pot
    # 2: 2.5 Pot
    # 2: 4 Pot


    RAISE_SIZE = [2/3, 1.5, 2.5, 4]
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


        self.distribution = [[[] for _ in range(9)] for _ in range(4)]
        for i in range(4):
            for j in range(9):
                self.distribution[i][j] = self.starting_distribution.copy()
        self.b_distribution = [[[] for _ in range(9)] for _ in range(4)]
        for i in range(4):
            for j in range(9):
                self.b_distribution[i][j] = self.starting_bet_distribution.copy()
        self.r_distribution = [[[] for _ in range(9)] for _ in range(4)]
        for i in range(4):
            for j in range(9):
                self.r_distribution[i][j] = self.starting_raise_distribution.copy()
        



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
        strength = Evaluator.evaluate_rank(self.cards, board)

        self.cur_strength = strength
        
        # dist represents the distribution we are using, b represents whether we are facing a bet or not
        def determine_action(dist, b, stage, stren):
            
            r = random.choices(self.ACTIONS, weights=tuple(dist), k = 1)

            if b:
                if r >= self.BET_1 and r <= self.BET_8 or r == self.CHECK:
                    self.determine_action(dist, b)
                elif r == self.CALL:
                    return (self.CALL, 0)
                elif r == self.FOLD:
                    return (self.FOLD, 0)
                elif r == self.RAISE_1:
                    return (self.RAISE_1, self.raise_dt[self.RAISE_1])
                elif r == self.RAISE_2:
                    return (self.RAISE_2, self.raise_dt[self.RAISE_2])
                elif r == self.RAISE_3:
                    return (self.RAISE_2, self.raise_dt[self.RAISE_3])
                elif r == self.RAISE_4:
                    return (self.RAISE_2, self.raise_dt[self.RAISE_4])
            else:
                if r >= self.RAISE_1 and r <= self.RAISE_4 or r == self.FOLD or r == self.CALL:
                    determine_action(dist, b)
                elif r == self.CHECK:
                    return (self.CHECK, 0)
                elif r == self.BET_1:
                    return (self.BET_1, self.bet_dt[self.BET_1])
                elif r == self.BET_2:
                    return (self.BET_2, self.bet_dt[self.BET_2])
                elif r == self.BET_3:
                    return (self.BET_3, self.bet_dt[self.BET_3])
                elif r == self.BET_4:
                    return (self.BET_4, self.bet_dt[self.BET_4])
                elif r == self.BET_5:
                    return (self.BET_5, self.bet_dt[self.BET_5])
                elif r == self.BET_6:
                    return (self.BET_6, self.bet_dt[self.BET_6])
                
                    

        if len(board) == 0:
            strength = strength.starting_eval(Evaluator.prime_product_rank(self.cards))
            dist = self.distribution[self.PREFLOP][strength]
            return determine_action(dist, bets[0] == bets[1] and bets[0] == 0, self.PREFLOP, strength)
        elif len(board) == 3:
            strength = strength.rank_breakdown(Evaluator.evaluate_rank(self.cards, board))
            dist = self.distribution[self.FLOP][strength]
            return determine_action(dist, bets[0] == bets[1] and bets[0] == 0, self.FLOP, strength)
        elif len(board) == 4:
            strength = strength.rank_breakdown(Evaluator.evaluate_rank(self.cards, board))
            dist = self.distribution[self.TURN][strength]
            return determine_action(dist, bets[0] == bets[1] and bets[0] == 0, self.TURN, strength)
        elif len(board) == 5:
            strength = strength.rank_breakdown(Evaluator.evaluate_rank(self.cards, board))
            dist = self.distribution[self.RIVER][strength]
            return determine_action(dist, bets[0] == bets[1] and bets[0] == 0, self.RIVER, strength)
        
            


        # bound_1 = self.fold_probability
        # bound_2 = self.fold_probability + self.raise_probability
        # if 0.0 < dice_roll <= bound_1:
        #     return Player.FOLD
        # elif bound_1 < dice_roll <= bound_2:
        #     return Player.RAISE
        # else:
        #     return Player.CALL
    

        


    def __repr__(self):
        return '<n_bigblinds={}, cards={}, folded={}>'.format(
            self.n_bigblinds,
            self.cards,
            not self.is_active)

# a class containing all distributions of a player


