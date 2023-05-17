from evaluator import Evaluator
import math

def is_squarer(integer):
    root = math.sqrt(integer)
    return integer == int(root + 0.5) ** 2

# Starting Hand breakdown
# 0. Best Startings (AA, KK)
# 1. Second Premiums (AK, QQ)
# 2. Third Premiums (JJ, 1010, AQ)
# 3. Two High Cards, 99 88 
# 4. Remaining Pocket Pairs (77, 66 ...)
# 5. Rest of the Crowd

def starting_eval(integer):
    if integer == 41 ** 2 or integer == 37 ** 2:
        return 0
    if integer == 31 ** 2 or integer == 29 ** 2:
        return 1
    if integer == 23 ** 2 or integer == 19 ** 2 or integer == 41 * 31:
        return 2
    if integer > 23 ** 2 or integer == 17 ** 2 or integer == 13 ** 2:
        return 3
    if is_squarer(integer):
        return 4
    return 5

PREFLOP = 0
FLOP = 1
TURN = 2
RIVER = 3

# Best 5 Cards breakdown
# 0. Straight Flush
# 1. Quads
# 2. Full House
# 3. Flush
# 4. Straight
# 5. Trips
# 6. Two Pair
# 7. Pair
# 8. High Card

def rank_breakdown(rank):
    if rank <= 10:
        return 0
    if rank <= 166:
        return 1
    if rank <= 322:
        return 2
    if rank <= 332:
        return 3
    if rank <= 1599:
        return 4
    if rank <= 2458:
        return 5
    if rank <= 3316:
        return 6
    if rank <= 6176:
        return 7
    return 8

