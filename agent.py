class Agent:
    """
    Create agent.
    ...

    Attributes
    ----------
    strategy : Dict[str, Dict[str, int]]
        The preflop strategy for an agent.
    regret : Dict[str, Dict[strategy, int]]
        The regret for an agent.
    """

    def __init__(self):
        """Construct an agent."""
        self.strategy = {}
        self.regret = {}
