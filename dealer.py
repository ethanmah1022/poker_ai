from typing import List
from card import Card
from player import Player
import random


class Dealer(object):
    """The dealer is in charge of handling the cards on a poker table."""

    def __init__(self):
        self.deck = [Card(rank, suit)
                     for suit in Card.SUITS for rank in Card.RANKS]
        random.shuffle(self.deck)
        self.board = []

    def reset_deck(self):
        """Resets deck to contain all 52 cards, and re-shuffled"""
        self.deck = [Card(rank, suit)
                     for suit in Card.SUITS for rank in Card.RANKS]
        random.shuffle(self.deck)

    def deal_card(self):
        """Return top card from deck."""
        return self.deck.pop(0)

    def deal_private_cards(self, players: List[Player]):
        """Deal private card to players.

        Parameters
        ----------
        players : list of Player
            The players to deal the private cards to.
        """
        for _ in range(2):
            for player in players:
                card = self.deal_card()
                player.cards.append(card)

    def deal_community_cards(self, n_cards: int):
        """Deal public cards."""
        if n_cards <= 0:
            raise ValueError(
                f"Positive n of cards must be specified, but got {n_cards}"
            )
        for _ in range(n_cards):
            card = self.deal_card()
            self.board.append(card)

    def deal_flop(self):
        """Deal the flop public cards to the `table`."""
        self.deck.pop(0)
        return self.deal_community_cards(3)

    def deal_turn(self):
        """Deal the turn public cards to the `table`."""
        self.deck.pop(0)
        return self.deal_community_cards(1)

    def deal_river(self):
        """Deal the river public cards to the `table`."""
        self.deck.pop(0)
        return self.deal_community_cards(1)
