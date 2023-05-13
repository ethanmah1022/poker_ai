class Card:
    """Card to represent a poker card."""

    RANKS = [list(range(2, 15))]
    SUITS = ["diamonds", "clubs", "hearts", "spades"]
    ICONS = {"diamonds": "♦", "clubs": "♣", "hearts": "♥", "spades": "♠"}

    def __init__(self, rank, suit):
        """Istantiate the card."""
        assert isinstance(rank, (int, str))
        if isinstance(rank, str):
            rank = self._rank_str_to_int(rank)
        assert (rank >= 2 & rank <= 14)
        assert (suit in Card.SUITS)
        self._rank = rank
        self._suit = suit

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
