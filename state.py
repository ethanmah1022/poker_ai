import collections
import copy
import json
import logging
import operator
import os
from typing import Any, Dict, List, Optional, Tuple

import joblib

from card import Card
from engine import GameEngine
from player import Player

InfoSetLookupTable = Dict[str, Dict[Tuple[int, ...], str]]


class PokerState(object):
    """The state of a poker game at some given point in time.

    The class is immutable and new state can be instantiated from once an
    action is applied via the `PokerState.new_state` method.
    """

    def __init__(self, players: List[Player]):
        """Initialise state."""
        assert(len(players) == 2)

        self._poker_engine = GameEngine(players)
        self._n_bigblinds = players[0].n_bigblinds

        # Setup game
        self._poker_engine.round_setup()
        self._current_bets = [0.5, 1]
        self._poker_engine.dealer.deal_private_cards(
            self._poker_engine.players)
        self._history: Dict[str, List[str]] = collections.defaultdict(list)
        self._betting_stage = "PREFLOP"
        self._betting_stage_to_round: Dict[str, int] = {
            "PREFLOP": 0,
            "FLOP": 1,
            "TURN": 2,
            "RIVER": 3,
            "SHOWDOWN": 4,
        }
        player_i_order: List[int] = [p_i for p_i in range(len(players))]
        self._player_i_lut: Dict[str, List[int]] = {
            "PREFLOP": player_i_order,
            "FLOP": player_i_order[1:] + player_i_order[:1],
            "TURN": player_i_order[1:] + player_i_order[:1],
            "RIVER": player_i_order[1:] + player_i_order[:1],
            "SHOWDOWN": player_i_order[1:] + player_i_order[:1],
            "TERMINAL": player_i_order[1:] + player_i_order[:1],
        }
        self._first_move_of_current_round = True
        self._reset_betting_round_state()
        for player in self.players:
            player.is_turn = False
        self.current_player.is_turn = True

    def __repr__(self):
        """Return a helpful description of object in strings and debugger."""
        return f"<ShortDeckPokerState player_i={self.player_i} betting_stage={self._betting_stage}>"

    def apply_action(self, action):
        """Create a new state after applying an action.
        Parameters
        ----------
        action_str : str or None
            The description of the action the current player is making. Can be
            any of {"fold, "call", "raise"}, the latter two only being possible
            if the agent hasn't folded already.

        Returns
        -------
        action : int
            One of Player.ACTIONS.
        new_state : PokerState
            A poker state instance that represents the game in the next
            timestep, after the action has been applied.
        """
        # Deep copy the parts of state that are needed that must be immutable
        # from state to state.
        new_state = copy.deepcopy(self)
        # An action has been made, so alas we are not in the first move of the
        # current betting round.
        new_state._first_move_of_current_round = False
        add_to_pot = 0
        if action == Player.CALL:
            add_to_pot = self._current_bets[(
                self.player_i+1) % 2] - self._current_bets[self.player_i]
            self._current_bets[self.player_i] = self._current_bets[(
                self.player_i+1) % 2]
        elif action in Player.ACTIONS_BET:
            add_to_pot = Player.bet_dict[action] * self._poker_engine.pot
            self._current_bets[self.player_i] += Player.bet_dict[action] * \
                self._poker_engine.pot
        elif action in Player.ACTIONS_RAISE:
            add_to_pot = Player.raise_dict[action] * self._poker_engine.pot
            self._current_bets[self.player_i] += Player.raise_dict[action] * \
                self._poker_engine.pot
        elif action == Player.FOLD:
            new_state.current_player.is_active = False
        new_state._current_bets = self._current_bets
        new_state.current_player.n_bigblinds -= add_to_pot
        new_state._poker_engine.pot += add_to_pot

        # Update the new state.
        new_state._history[new_state.betting_stage].append(action)
        new_state._n_actions += 1
        # Player has made move, increment the player that is next.
        while True:
            new_state._move_to_next_player()
            # If we have finished betting, (i.e: All players have put the
            # same amount of chips in), then increment the stage of
            # betting.

            finished_betting = not(
                new_state._poker_engine.more_betting_needed(self._current_bets))
            if finished_betting and new_state.all_players_have_actioned:
                # We have done atleast one full round of betting, increment
                # stage of the game.
                new_state._increment_stage()
                new_state._reset_betting_round_state()
                new_state._current_bets = [0, 0]
                new_state._first_move_of_current_round = True
            # print("BOOLEAN2: ", new_state.current_player.is_active)
            # if not new_state.current_player.is_active:
            #     new_state._betting_stage = "TERMINAL"
            #     break
            if new_state.current_player.is_active:
                if new_state._poker_engine.n_players_with_moves == 1:
                    # No players left.
                    new_state._betting_stage = "TERMINAL"
                    if not new_state._poker_engine.dealer.board:
                        new_state._poker_engine.dealer.deal_flop()
                # Now check if the game is terminal.
                if new_state._betting_stage in {"TERMINAL", "SHOWDOWN"}:
                    # Distribute winnings.
                    new_state._poker_engine.compute_winners()
                break
        for player in new_state.players:
            player.is_turn = False
        new_state.current_player.is_turn = True
        return new_state

    def _move_to_next_player(self):
        """Ensure state points to next valid active player."""
        self._player_i_index += 1
        if self._player_i_index >= len(self.players):
            self._player_i_index = 0

    def _reset_betting_round_state(self):
        """Reset the state related to counting types of actions."""
        self._all_players_have_made_action = False
        self._current_bets == [0, 0]
        self._n_actions = 0
        self._n_raises = 0
        self._player_i_index = 0
        self._n_players_started_round = self._poker_engine.n_active_players
        while not self.current_player.is_active:
            self._player_i_index += 1

    def _increment_stage(self):
        """Once betting has finished, increment the stage of the poker game."""
        # Progress the stage of the game.
        if self._betting_stage == "PREFLOP":
            # Progress from private cards to the flop.
            self._betting_stage = "FLOP"
            self._poker_engine.dealer.deal_flop()
        elif self._betting_stage == "FLOP":
            # Progress from flop to turn.
            self._betting_stage = "TURN"
            self._poker_engine.dealer.deal_turn()
        elif self._betting_stage == "TURN":
            # Progress from turn to river.
            self._betting_stage = "RIVER"
            self._poker_engine.dealer.deal_river()
        elif self._betting_stage == "RIVER":
            # Progress to the showdown.
            self._betting_stage = "SHOWDOWN"
        elif self._betting_stage in {"SHOWDOWN", "SHOWDOWN"}:
            pass
        else:
            raise ValueError(f"Unknown betting_stage: {self._betting_stage}")

    @property
    def private_hands(self) -> Dict[Player, List[Card]]:
        """Return all private hands."""
        return {p: p.cards for p in self.players}

    @property
    def initial_regret(self) -> Dict[str, float]:
        """Returns the default regret for this state."""
        return {action: 0 for action in self.legal_actions}

    @property
    def initial_strategy(self) -> Dict[str, float]:
        """Returns the default strategy for this state."""
        return {action: 0 for action in self.legal_actions}

    @property
    def betting_stage(self) -> str:
        """Return betting stage."""
        return self._betting_stage

    @property
    def all_players_have_actioned(self) -> bool:
        """Return whether all players have made atleast one action."""
        return self._n_actions >= self._n_players_started_round

    @property
    def n_players_started_round(self) -> bool:
        """Return n_players that started the round."""
        return self._n_players_started_round

    @property
    def player_i(self) -> int:
        """Get the index of the players turn it is."""
        return self._player_i_lut[self._betting_stage][self._player_i_index]

    @player_i.setter
    def player_i(self, _: Any):
        """Raise an error if player_i is set."""
        raise ValueError(f"The player_i property should not be set.")

    @property
    def betting_round(self) -> int:
        """Betting stage in integer form."""
        try:
            betting_round = self._betting_stage_to_round[self._betting_stage]
        except KeyError:
            raise ValueError(
                f"Attemped to get betting round for stage "
                f"{self._betting_stage} but was not supported in the lut with "
                f"keys: {list(self._betting_stage_to_round.keys())}"
            )
        return betting_round

    @property
    def info_set(self) -> str:
        """Get the information set for the current player."""
        # Convert history from a dict of lists to a list of dicts as I'm
        # paranoid about JSON's lack of care with insertion order.
        info_set_dict = {
            "history": [
                {betting_stage: [action for action in actions]}
                for betting_stage, actions in self._history.items()
            ],
        }
        return json.dumps(info_set_dict, separators=(",", ":"))

    @property
    def is_terminal(self) -> bool:
        """Returns whether this state is terminal or not.

        The state is terminal once all rounds of betting are complete and we
        are at the show down stage of the game or if all players have folded.
        """
        return self._betting_stage in {"SHOWDOWN", "TERMINAL"}

    @property
    def players(self) -> List[Player]:
        """Returns players in table."""
        return self._poker_engine.players

    @property
    def current_player(self) -> Player:
        """Returns a reference to player that makes a move for this state."""
        return self._poker_engine.players[self.player_i]

    @property
    def payout(self) -> Dict[int, int]:
        """Return player index to payout number of chips dictionary."""
        n_chips_delta = dict()
        for player_i, player in enumerate(self.players):
            n_chips_delta[player_i] = player.n_bigblinds - self._n_bigblinds
        return n_chips_delta

    @property
    def legal_actions(self) -> List[Optional[str]]:
        """Return the actions that are legal for this game state."""
        actions: List[Optional[str]] = []
        if self.current_player.is_active:
            if self._betting_stage == "PREFLOP" and self._current_bets == [1, 1]:
                actions += [Player.CHECK] + Player.ACTIONS_RAISE
            elif self._current_bets == [0, 0]:
                # check, bet 1/3,1/2,2/3,1,2x pot
                actions += [Player.CHECK] + Player.ACTIONS_BET
            else:
                actions += [Player.FOLD, Player.CALL] + Player.ACTIONS_RAISE
        else:
            actions += [None]
        return actions
