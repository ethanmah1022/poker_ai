import logging
import random
from pathlib import Path
from typing import Dict

import click
import joblib
import yaml
from tqdm import tqdm, trange

from agent import Agent
import ai
import utils
from state import PokerState
from player import Player


def print_strategy(strategy: Dict[str, Dict[str, int]]):
    """
    Print strategy.

    ...

    Parameters
    ----------
    strategy : Dict[str, Dict[str, int]]
        The preflop strategy for our agent.
    """
    for info_set, action_to_probabilities in sorted(strategy.items()):
        norm = sum(list(action_to_probabilities.values()))
        tqdm.write(f"{info_set}")
        for action, probability in action_to_probabilities.items():
            tqdm.write(f"  - {action}: {probability / norm:.2f}")


def simple_search(
    config: Dict[str, int],
    save_path: Path,
    strategy_interval: int,
    n_iterations: int,
    lcfr_threshold: int,
    discount_interval: int,
    c: int,
    dump_iteration: int,
    update_threshold: int,
):
    """
    Train agent.

    ...

    Parameters
    ----------
    config : Dict[str, int],
        Configurations for the simple search.
    save_path : str
        Path to save to.
    strategy_interval : int
        Iteration at which to update strategy.
    n_iterations : int
        Number of iterations.
    lcfr_threshold : int
        Iteration at which to begin linear CFR.
    discount_interval : int
        Iteration at which to discount strategy and regret.
    c : int
        Floor for regret at which we do not search a node.
    n_players : int
        Number of players.
    dump_iteration : int
        Iteration at which we begin serialization.
    update_threshold : int
        Iteration at which we begin updating strategy.
    """
    agent = Agent()
    for t in trange(1, n_iterations + 1, desc="train iter"):
        if t == 2:
            logging.disable(logging.DEBUG)
        for i in range(2):  # fixed position i
            # Create a new state.
            players = [Player(300) for _ in range(2)]
            state: PokerState = PokerState(players)
            if t > update_threshold and t % strategy_interval == 0:
                ai.update_strategy(agent=agent, state=state, i=i, t=t)
            ai.cfr(agent=agent, state=state, i=i, t=t)
        if t < lcfr_threshold & t % discount_interval == 0:
            d = (t / discount_interval) / ((t / discount_interval) + 1)
            for I in agent.regret.keys():
                for a in agent.regret[I].keys():
                    agent.regret[I][a] *= d
                    agent.strategy[I][a] *= d
        if (t > update_threshold) & (t % dump_iteration == 0):
            # dump the current strategy (sigma) throughout training and then
            # take an average. This allows for estimation of expected value in
            # leaf nodes later on using modified versions of the blueprint
            # strategy.
            ai.serialise(
                agent=agent, save_path=save_path, t=t, server_state=config,
            )

    print_strategy(agent.strategy)


if __name__ == "__main__":
    train()
