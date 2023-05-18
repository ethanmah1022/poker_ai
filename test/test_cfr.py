import pytest


def test_cfr():
    import ai
    from agent import Agent
    from state import PokerState
    from player import Player
    agent = Agent()
    players = [Player(100) for _ in range(2)]
    state: PokerState = PokerState(players)
    for t in range(0, 200):
        for i in range(1):
            ai.cfr(agent=agent, state=state, i=i, t=t)
