import pytest


def test_hand():
    """Test a hand can be played."""
    from poker_ai.player import Player
    from poker_ai.engine import GameEngine
    initial_bigblinds = 300
    michael = Player(initial_bigblinds)
    ethan = Player(initial_bigblinds)
    players = [michael, ethan]
    engine = GameEngine(players)
    engine.play_one_round()
