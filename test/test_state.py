import pytest


def test_state():
    """Test a PokerState object is working properly."""
    from player import Player
    from state import PokerState
    initial_bigblinds = 300
    michael = Player(initial_bigblinds)
    ethan = Player(initial_bigblinds)
    players = [michael, ethan]
    state = PokerState(players)

    assert(state.players[0].n_bigblinds == 299.5)
    assert(state.players[1].n_bigblinds == 299)
    assert(state._poker_engine.pot == 1.5)
    assert(state._current_bets == [0.5, 1])
    for i in range(2):
        assert(len(state.players[i].cards) == 2)
    assert(state._poker_engine.dealer.board == [])
    assert(state.legal_actions == [
           Player.FOLD, Player.CALL] + Player.ACTIONS_RAISE)
    state2 = state.apply_action(Player.CALL)
    assert(state2._poker_engine.pot == 2)
    assert(state2.players[0].n_bigblinds == 299)
    assert(state2._betting_stage == "PREFLOP")
    assert(state2._current_bets == [1, 1])
    assert(state2.legal_actions == [Player.CHECK] + Player.ACTIONS_RAISE)
    state3 = state2.apply_action(Player.RAISE_2)
    assert(state3._poker_engine.pot == 6)
    assert(state3._current_bets == [1, 5])
    assert(state3.players[1].n_bigblinds == 295)
    assert(state3.legal_actions == [
           Player.FOLD, Player.CALL] + Player.ACTIONS_RAISE)
    state4 = state3.apply_action(Player.CALL)
    assert(state4._betting_stage == "FLOP")  # pot is 10, reach the flop
    assert(state4._current_bets == [0, 0])
    assert(len(state4._poker_engine.dealer.board) == 3)
    assert(state4.legal_actions == [Player.CHECK] + Player.ACTIONS_BET)
    state5 = state4.apply_action(Player.CHECK)
    state6 = state5.apply_action(Player.CHECK)
    assert(state6._betting_stage == "TURN")  # pot is 10, reach the turn
    assert(state6._current_bets == [0, 0])
    assert(len(state6._poker_engine.dealer.board) == 4)
    assert(state6.legal_actions == [Player.CHECK] + Player.ACTIONS_BET)
    assert(state6._poker_engine.pot == 10)
    state7 = state6.apply_action(Player.CHECK)
    state8 = state7.apply_action(Player.CHECK)
    assert(state8._betting_stage == "RIVER")  # pot is 10, reach the river
    assert(state8._current_bets == [0, 0])
    assert(len(state8._poker_engine.dealer.board) == 5)
    state9 = state8.apply_action(Player.CHECK)
    state10 = state9.apply_action(Player.BET_2)
    assert(state10.player_i == 1)
    # not [0,5] because SB who acts 2nd bets 5
    assert(state10._current_bets == [5, 0])
    assert(state10.players[0].n_bigblinds == 290)
    assert(state10.players[1].n_bigblinds == 295)
    assert(state10.legal_actions == [
           Player.FOLD, Player.CALL] + Player.ACTIONS_RAISE)
    assert(state10._betting_stage == "RIVER")
    state11a = state10.apply_action(Player.CALL)
    assert(state11a._betting_stage == "SHOWDOWN")
    assert(state11a._poker_engine.pot == 20)
    assert(state11a.players[0].n_bigblinds ==
           310 or state11a.players[1].n_bigblinds == 310)
    assert(state11a.payout == {0: 10, 1: -10}
           or state11a.payout == {0: -10, 1: 10})
    state11b = state10.apply_action(Player.FOLD)
    assert(state11b._betting_stage == "TERMINAL")
    assert(state11b._poker_engine.pot == 15)
    assert(state11b.players[0].n_bigblinds == 305)
    assert(state11b.payout == {0: 5, 1: -5})
