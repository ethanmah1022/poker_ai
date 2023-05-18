from copy import deepcopy
from typing import List
from player import Player
from evaluator import Evaluator
from dealer import Dealer
import logging


class GameEngine(object):
    """Instance to represent the lifetime of a full poker hand.

    A hand of poker is played at a table by playing for betting rounds:
    pre-flop, flop, turn and river. 
    """

    def __init__(self, players: List[Player]):
        # Set up rules of poker game
        self.root = None
        assert(len(players) == 2)
        self.players = players
        self.dealer = Dealer()
        self.handeval = Evaluator.evaluate_rank
        self.pot = 0

    def play_one_round(self):
        """"""
        self.round_setup()
        self._all_dealing_and_betting_rounds()
        self.compute_winners()
        self.round_cleanup()

    def round_setup(self):
        """Code that must be done to setup the round before the game starts."""
        self.pot = 0  # set pot to 0
        self.players.append(self.players.pop(0))  # rotate order
        self.players[0].n_bigblinds -= 0.5  # put in blinds
        self.players[1].n_bigblinds -= 1
        self.pot += 1.5

    def _all_dealing_and_betting_rounds(self):
        """Run through dealing of all cards and all rounds of betting."""
        self.dealer.deal_private_cards(self.players)
        self._betting_round(first_round=True)
        self.dealer.deal_flop()
        self._betting_round()
        self.dealer.deal_turn()
        self._betting_round()
        self.dealer.deal_river()
        self._betting_round()

    def n_players_with_moves(self) -> int:
        """Returns the amount of players that can freely make a move."""
        return sum(p.is_active and not p.is_all_in for p in self.players)

    def _betting_round(self, first_round: bool = False):
        """Computes the round(s) of betting.

        Until the current betting round is complete, all active players take
        actions in the order they were placed at the table. A betting round
        lasts until all players either call the highest placed bet or fold.
        """
        if self.n_players_with_moves > 1:  # if both players can act
            self._bet_until_everyone_has_bet_evenly()
            # logger.debug(
            #     f"Finished round of betting, {self.n_active_players} active "
            #     f"players, {self.n_all_in_players} all in players."
            # )
        else:
            pass
            # logger.debug("Skipping betting as no players are free to bet.")

    def more_betting_needed(self, bets) -> bool:
        """Returns if more bets are required to terminate betting.

        If all active players have settled, i.e everyone has called the highest
        bet or folded, the current betting round is complete, else, more
        betting is required from the active players that are not all in.
        """
        all_active = self.players[0].is_active and self.players[1].is_active
        return not(bets[0] == bets[1]) and all_active

    def _bet_until_everyone_has_bet_evenly(self):
        """Iteratively bet until all have put the same num chips in the pot."""
        # Ensure for the first move we do one round of betting.
        first_round = True
        # logger.debug("Started round of betting.")
        bets = [0, 0]
        while first_round or self.more_betting_needed(bets):
            self._all_active_players_take_action(first_round, bets)
            first_round = False
            # logger.debug(f"> Betting iter, total: {sum(self.all_bets)}")
        self.pot += sum(bets)

    def _all_active_players_take_action(self, first_round: bool, bets):
        """Force all players to make a move."""
        for idx, player in self._players_in_order_of_betting(first_round):
            if player.is_active:
                action = player.take_action(self.dealer.board, bets)
                if action == Player.CHECK:
                    pass
                elif action == Player.BET:
                    bet_amount = 25  # must be returned from take_action
                    player.n_bigblinds -= bet_amount
                    bets[idx] += bet_amount
                elif action == Player.CALL:
                    player.n_bigblinds -= bets[(idx+1) % 2]-bets[idx]
                    bets[idx] = bets[(idx+1) % 2]
                elif action == Player.RAISE:
                    # again, must be returned from take_action
                    raise_amount = sum(bets) * 2.5
                    # raise_amount is difference from initial bet, NOT total bet
                    player.n_bigblinds -= bets[(idx+1) % 2] + raise_amount
                    bets[idx] += raise_amount
                elif action == Player.FOLD:
                    player.is_active = False

                # unsure about this entire segment, apparently take_action is
                # coded by CFR?

    def compute_winners(self):
        """Compute winners and payout the chips to respective players."""
        # If one player already inactive due to folding, give pot to active player
        if not (self.players[0].is_active and self.players[1].is_active):
            if self.players[0].is_active:
                self.players[0].n_bigblinds += self.pot
            else:
                self.players[1].n_bigblinds += self.pot
        else:  # both players active, compare rankings
            first_player_rank = self.handeval(
                self.players[0].cards, self.dealer.board)
            second_player_rank = self.handeval(
                self.players[1].cards, self.dealer.board)
            if first_player_rank < second_player_rank:  # only add to winners
                self.players[0].n_bigblinds += self.pot
            elif first_player_rank > second_player_rank:
                self.players[1].n_bigblinds += self.pot
            else:  # chop pot
                self.players[0].n_bigblinds += self.pot/2
                self.players[1].n_bigblinds += self.pot/2

    def _players_in_order_of_betting(self, first_round: bool) -> List[Player]:
        """Players bet in different orders depending on the round it is."""
        if first_round:
            return self.players[1:] + self.players[:1]
        return self.players

    def round_cleanup(self):
        """Resetting board, deck, and player's cards."""
        self.dealer.reset(self.players)

    @property
    def n_players_with_moves(self) -> int:
        """Returns the amount of players that can freely make a move."""
        return sum(p.is_active and not p.is_all_in() for p in self.players)

    @property
    def n_active_players(self) -> int:
        """Returns the number of active players."""
        return sum(p.is_active for p in self.players)

    @property
    def n_all_in_players(self) -> int:
        """Return the amount of players that are active and that are all in."""
        return sum(p.is_active and p.is_all_in for p in self.players)
