class Card:
    """Card to represent a poker card."""

    def __init__(self, rank, suit):
        """Instanciate the card."""
        self._rank = rank
        self._suit = suit
        rank_char = self._rank_to_char(rank)
        suit_char = self.suit.lower()[0]
        self._eval_card = EvaluationCard.new(f"{rank_char}{suit_char}")
