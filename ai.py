
import copy
import joblib
import os
from pathlib import Path
from typing import Dict, List, Union
import numpy as np

from agent import Agent
from state import PokerState


def calculate_strategy(this_info_sets_regret: Dict[str, float]) -> Dict[str, float]:
    """
    Calculate the strategy based on the current information sets regret.
    Based off http://modelai.gettysburg.edu/2013/cfr/cfr.pdf pages 9-11
    ...

    Parameters
    ----------
    this_info_sets_regret : Dict[str, float]
        Regret for each action at this info set.

    Returns
    -------
    strategy : Dict[str, float]
        Strategy as a probability over actions.

        A strategy sigma_i for player i maps each player i, information set I_i,
        and legal player i action a ∈ A(I_i) to the probability that the player 
        will choose a in I_i at time t. All player strategies together at time t
        form a strategy profile sigma_t .

    """
    actions = this_info_sets_regret.keys()
    regret_sum = sum([max(regret, 0)
                     for regret in this_info_sets_regret.values()])
    if regret_sum > 0:
        strategy: Dict[str, float] = {
            action: max(this_info_sets_regret[action], 0) / regret_sum
            for action in actions
        }
    else:
        default_probability = 1 / len(actions)
        strategy: Dict[str, float] = {
            action: default_probability for action in actions}
    return strategy


def update_strategy(
    agent: Agent,
    state: PokerState,
    i: int,
    t: int
):
    """
    Update pre flop strategy using a more theoretically sound approach.

    ...

    Parameters
    ----------
    agent : Agent
        Agent being trained.
    state : ShortDeckPokerState
        Current game state.
    i : int
        The Player.
    t : int
        The iteration.
    locks : Dict[str, mp.synchronize.Lock]
        The locks for multiprocessing
    """
    ph = state.player_i  # this is always the case no matter what i is

    player_not_in_hand = not state.players[i].is_active
    if state.is_terminal or player_not_in_hand or state.betting_round > 0:
        return

    # NOTE(fedden): According to Algorithm 1 in the supplementary material,
    #               we would add in the following bit of logic. However we
    #               already have the game logic embedded in the state class,
    #               and this accounts for the chance samplings. In other words,
    #               it makes sure that chance actions such as dealing cards
    #               happen at the appropriate times.
    # elif h is chance_node:
    #   sample action from strategy for h
    #   update_strategy(rs, h + a, i, t)

    elif ph == i:
        # calculate regret
        this_info_sets_regret = agent.regret.get(
            state.info_set, state.initial_regret)
        sigma = calculate_strategy(this_info_sets_regret)
        # choose an action based of sigma
        available_actions: List[str] = list(sigma.keys())
        action_probabilities: np.ndarray = np.array(list(sigma.values()))
        action: str = np.random.choice(
            available_actions, p=action_probabilities)
        # Increment the action counter.
        this_states_strategy = agent.strategy.get(
            state.info_set, state.initial_strategy
        )
        this_states_strategy[action] += 1
        # Update the master strategy by assigning.
        agent.strategy[state.info_set] = this_states_strategy
        new_state: PokerState = state.apply_action(action)
        update_strategy(agent, new_state, i, t)
    else:
        # Traverse each action.
        for action in state.legal_actions:
            new_state: PokerState = state.apply_action(action)
            update_strategy(agent, new_state, i, t)


def cfr(agent: Agent, state: PokerState, i: int, t: int,):
    """
    Regular counterfactual regret minimization algorithm.

    Parameters
    ----------
    agent : Agent
        Agent being trained.
    state : PokerState
        Current game state, encapsulates info like history of actions.
    i : int
        The Player.
    t : int
        The time-step/iteration.
    """
    ph = state.player_i

    player_not_in_hand = not state.players[i].is_active
    if state.is_terminal or player_not_in_hand:  # if hand has terminated
        return state.payout[i]
    elif ph == i:
        # calculate strategy
        this_info_sets_regret = agent.regret.get(
            state.info_set, state.initial_regret)
        sigma = calculate_strategy(this_info_sets_regret)

        vo = 0.0
        voa: Dict[str, float] = {}
        for action in state.legal_actions:
            new_state: PokerState = state.apply_action(action)
            voa[action] = cfr(agent, new_state, i, t)
            vo += sigma[action] * voa[action]

        this_info_sets_regret = agent.regret.get(
            state.info_set, state.initial_regret)
        for action in state.legal_actions:
            this_info_sets_regret[action] += voa[action] - vo
        # Assign regret back to the shared memory.
        agent.regret[state.info_set] = this_info_sets_regret
        return vo
    else:
        this_info_sets_regret = agent.regret.get(
            state.info_set, state.initial_regret)
        sigma = calculate_strategy(this_info_sets_regret)
        available_actions: List[str] = list(sigma.keys())
        action_probabilities: List[float] = list(sigma.values())
        action: str = np.random.choice(
            available_actions, p=action_probabilities)
        new_state: PokerState = state.apply_action(action)
        return cfr(agent, new_state, i, t)


def serialise(
    agent: Agent,
    save_path: Path,
    t: int,
    server_state: Dict[str, Union[str, float, int, None]]
):
    """
    Write progress of optimising agent (and server state) to file.

    ...

    Parameters
    ----------
    agent : Agent
        Agent being trained.
    save_path : ShortDeckPokerState
        Current game state.
    t : int
        The iteration.
    server_state : Dict[str, Union[str, float, int, None]]
        All the variables required to resume training.
    locks : Dict[str, mp.synchronize.Lock]
        The locks for multiprocessing
    """
    # Load the shared strategy that we accumulate into.
    agent_path = os.path.abspath(str(save_path / f"agent.joblib"))
    if os.path.isfile(agent_path):
        offline_agent = joblib.load(agent_path)
    else:
        offline_agent = {
            "regret": {},
            "timestep": t,
            "strategy": {},
            "pre_flop_strategy": {}
        }
    # Lock shared dicts so no other process modifies it whilst writing to
    # file.
    # Calculate the strategy for each info sets regret, and accumulate in
    # the offline agent's strategy.
    for info_set, this_info_sets_regret in sorted(agent.regret.items()):
        strategy = calculate_strategy(this_info_sets_regret)
        if info_set not in offline_agent["strategy"]:
            offline_agent["strategy"][info_set] = {
                action: probability for action, probability in strategy.items()
            }
        else:
            for action, probability in strategy.items():
                offline_agent["strategy"][info_set][action] += probability

    offline_agent["regret"] = copy.deepcopy(agent.regret)
    offline_agent["pre_flop_strategy"] = copy.deepcopy(agent.strategy)
    joblib.dump(offline_agent, agent_path)
    # Dump the server state to file too, but first update a few bits of the
    # state so when we load it next time, we start from the right place in
    # the optimisation process.
    server_path = save_path / f"server.gz"
    server_state["agent_path"] = agent_path
    server_state["start_timestep"] = t + 1
    joblib.dump(server_state, server_path)
