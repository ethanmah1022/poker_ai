class Card:
    """Card to represent a poker card."""

    RANKS = [list(range(2, 15))]
    SUITS = ["diamonds", "clubs", "hearts", "spades"]
    ICONS = {"diamonds": "♦", "clubs": "♣", "hearts": "♥", "spades": "♠"}
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
    SUIT_CHAR_TO_INT = {
        "spades": 1,  # spades 0001
        "hearts": 2,  # hearts 0010
        "diamonds": 4,  # diamonds 0100
        "clubs": 8,  # clubs 1000
    }

    def __init__(self, rank, suit):
        """Istantiate the card."""
        assert isinstance(rank, (int, str))
        if isinstance(rank, str):
            rank = self._rank_str_to_int(rank)
        assert (rank >= 2 and rank <= 14)
        assert (suit in Card.SUITS)
        self._rank = rank
        self._suit = suit
        self._rank_prime = Card.PRIMES[rank-2]
        self._suit_int = Card.SUIT_CHAR_TO_INT[suit]

    def _rank_str_to_int(self, string):
        """Convert rank from type string to type int"""
        return {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "jack": 11,
            "queen": 12,
            "king": 13,
            "ace": 14,
            "t": 10,
            "j": 11,
            "q": 12,
            "k": 13,
            "a": 14,
        }[string.lower()]

    def __lt__(self, other):
        return self.rank < other.rank

    def __le__(self, other):
        return self.rank <= other.rank

    def __gt__(self, other):
        return self.rank > other.rank

    def __ge__(self, other):
        return self.rank >= other.rank

    def __ne__(self, other):
        return (self.rank == other.rank) & (self.suit == other.suit)

    def getRank(self):
        return self._rank

    def getSuit(self):
        return self._suit

    def getRankPrime(self):
        return self._rank_prime

    def getSuitInt(self):
        return self._suit_binary

    def __repr__(self):
        rank_str = {
            2: "2",
            3: "3",
            4: "4",
            5: "5",
            6: "6",
            7: "7",
            8: "8",
            9: "9",
            10: "10",
            11: "J",
            12: "Q",
            13: "K",
            14: "A",
        }
        return rank_str[self._rank]+Card.ICONS[self._suit]
