import itertools

from card import Card
from lookuptables import flush_lookup, non_flush_lookup


def prime_product_rank(cards):
    """
    Returns the prime product from the list of cards.
    """
    product = 1
    for card in cards:
        product *= card.rank_prime
    return product


def evaluate(cards, board):
    """
    This is the function that the user calls to get a hand rank.

    Evaluates hand strengths using a variant of Cactus Kev's evaluator algorithm:
    http://suffe.cool/poker/evaluator.html

    Overall, evaluation is very fast as all calculations are done with bit 
    arithmetic and table lookups.
    """
    all_cards = [card for card in cards + board]
    num_cards = len(all_cards)
    if num_cards == 5:
        return(evaluate_five(all_cards))
    else:
        minimum = 7462 #lowest ranking possible
        combos = itertools.combinations(all_cards, 5)
        for combo in combos:
            rank = evaluate_five(combo)
            if rank < minimum:
                minimum = rank
        return minimum


def evaluate_five(cards):
    """
    Performs an evalution given 5-card hand, mapping them to a rank in the
    range [1, 7462], with lower ranks being more powerful. It is a variation
    of Cactus Kev's 5 card evaluator.
    """

    prime = prime_product_rank(cards)
    # if flush
    if cards[0].getSuitInt & cards[1].getSuitInt & cards[2].getSuitInt \
            & cards[3].getSuitInt & cards[4].getSuitInt & 0xF:
        return flush_lookup[prime]
    else:
        return non_flush_lookup[prime]

def get_rank_class(self, rank):
    """Returns the class of hand from the numerical hand ranking from evaluate."""
    if rank == 1:
        return "Royal Flush"
    elif rank <= 10:
        return "Straight Flush"
    elif rank <= 166:
        return "Four of a Kind"
    elif rank <= 322:
        return "Full House"
    elif rank <= 1599:
        return "Flush"
    elif rank <= 1609:
        return "Straight"
    elif rank <= 2467:
        return "Three of a Kind"
    elif rank <= 3325:
        return "Two Pair"
    elif rank <= 3325:
        return "Two Pair"
    elif rank <= 7462:
        return "One Pair"
    else:
        raise Exception("Inavlid hand rank, cannot return rank class")
   