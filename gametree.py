from copy import deepcopy

FOLD = 0
CALL = 1
RAISE = 2


class Node(object):
    def __init__(self, parent, committed, holecards, board, deck, bet_history):
        if parent:
            self.parent = parent
            self.parent.add_child(self)
        self.committed = deepcopy(committed)
        self.holecards = deepcopy(holecards)
        self.board = deepcopy(board)
        self.deck = deepcopy(deck)
        self.bet_history = deepcopy(bet_history)

    def add_child(self, child):
        if self.children is None:
            self.children = [child]
        else:
            self.children.append(child)


class TerminalNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, bet_history, payoffs, players_in):
        Node.__init__(self, parent, committed, holecards,
                      board, deck, bet_history)
        self.payoffs = payoffs
        self.players_in = deepcopy(players_in)


class HolecardChanceNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, bet_history, todeal):
        Node.__init__(self, parent, committed, holecards,
                      board, deck, bet_history)
        self.todeal = todeal
        self.children = []


class BoardcardChanceNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, bet_history, todeal):
        Node.__init__(self, parent, committed, holecards,
                      board, deck, bet_history)
        self.todeal = todeal
        self.children = []


class ActionNode(Node):
    def __init__(self, parent, committed, holecards, board, deck, bet_history, player, infoset_format):
        Node.__init__(self, parent, committed, holecards,
                      board, deck, bet_history)
        self.player = player
        self.children = []
        self.raise_action = None
        self.call_action = None
        self.fold_action = None
        self.player_view = infoset_format(
            player, holecards[player], board, bet_history)

    def valid(self, action):
        if action == FOLD:
            return self.fold_action
        if action == CALL:
            return self.call_action
        if action == RAISE:
            return self.raise_action
        raise Exception(
            "Unknown action {0}. Action must be FOLD, CALL, or RAISE".format(action))

    def get_child(self, action):
        return self.valid(action)
