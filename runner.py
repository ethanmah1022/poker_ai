"""Script for using multiprocessing to train agent.

CLI Use
-------

Below you can run `python runner.py --help` to get the following description of
the two commands available in the CLI, `resume` and `search`:
```
Usage: poker_ai train start [OPTIONS]

  Train agent from scratch.

Options:
  --strategy_interval INTEGER     Update the current strategy whenever the
                                  iteration % strategy_interval == 0.
  --n_iterations INTEGER          The total number of iterations we should
                                  train the model for.
  --lcfr_threshold INTEGER        A threshold for linear CFR which means don't
                                  apply discounting before this iteration.
  --discount_interval INTEGER     Discount the current regret and strategy
                                  whenever iteration % discount_interval == 0.
  --prune_threshold INTEGER       When a uniform random number is less than
                                  95%, and the iteration > prune_threshold,
                                  use CFR with pruning.
  --c INTEGER                     Pruning threshold for regret, which means
                                  when we are using CFR with pruning and have
                                  a state with a regret of less than `c`, then
                                  we'll elect to not recusrively visit it and
                                  it's child nodes.
  --n_players INTEGER             The number of players in the game.
  --dump_iteration INTEGER        When the iteration % dump_iteration == 0, we
                                  will compute a new strategy and write that
                                  to the accumlated strategy, which gets
                                  normalised at a later time.
  --update_threshold INTEGER      When the iteration is greater than
                                  update_threshold we can start updating the
                                  strategy.
  --lut_path TEXT                 The path to the files for clustering the
                                  infosets.
  --pickle_dir TEXT               Whether or not the lut files are pickle
                                  files. This lookup method is deprecated.
  --single_process / --multi_process
                                  Either use or don't use multiple processes.
  --sync_update_strategy / --async_update_strategy
                                  Do or don't synchronise update_strategy.
  --sync_cfr / --async_cfr        Do or don't synchronuse CFR.
  --sync_discount / --async_discount
                                  Do or don't synchronise the discounting.
  --sync_serialise / --async_serialise
                                  Do or don't synchronise the serialisation.
  --nickname TEXT                 The nickname of the study.
  --help                          Show this message and exit.
```
"""
import logging
from pathlib import Path
from typing import Dict

import click
import joblib
import yaml

import utils
from train import simple_search


log = logging.getLogger("runner")


@click.group()
def train():
    """Train a poker AI."""
    pass


@train.command()
@click.option(
    "--server_config_path",
    default="./server.gz",
    help="The path to the previous server.gz file from a previous study.",
)
def resume(server_config_path: str):
    """
    Continue training agent from config loaded from file.

    ...

    Parameters
    ----------
    server_config_path : str
        Path to server configurations.
    """
    try:
        config = joblib.load(server_config_path)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Server config file not found at the path: {server_config_path}\n "
            f"Please set the path to a valid file dumped by a previous session."
        )


@train.command()
@click.option(
    "--strategy_interval",
    default=20,
    help="Update the current strategy whenever the iteration % strategy_interval == 0.",
)
@click.option(
    "--n_iterations",
    default=1500,
    help="The total number of iterations we should train the model for.",
)
@click.option(
    "--lcfr_threshold",
    default=400,
    help=(
        "A threshold for linear CFR which means don't apply discounting "
        "before this iteration."
    ),
)
@click.option(
    "--discount_interval",
    default=400,
    help=(
        "Discount the current regret and strategy whenever iteration % "
        "discount_interval == 0."
    ),
)
@click.option(
    "--c",
    default=-20000,
    help=(
        "Pruning threshold for regret, which means when we are using CFR with "
        "pruning and have a state with a regret of less than `c`, then we'll "
        "elect to not recusrively visit it and it's child nodes."
    ),
)
@click.option("--n_players", default=3, help="The number of players in the game.")
@click.option(
    "--dump_iteration",
    default=20,
    help=(
        "When the iteration % dump_iteration == 0, we will compute a new strategy "
        "and write that to the accumlated strategy, which gets normalised at a "
        "later time."
    ),
)
@click.option(
    "--update_threshold",
    default=400,
    help=(
        "When the iteration is greater than update_threshold we can start "
        "updating the strategy."
    ),
)
@click.option(
    "--sync_update_strategy/--async_update_strategy",
    default=False,
    help="Do or don't synchronise update_strategy.",
)
@click.option(
    "--sync_cfr/--async_cfr", default=False, help="Do or don't synchronuse CFR."
)
@click.option(
    "--sync_discount/--async_discount",
    default=False,
    help="Do or don't synchronise the discounting.",
)
@click.option(
    "--sync_serialise/--async_serialise",
    default=False,
    help="Do or don't synchronise the serialisation.",
)
@click.option("--nickname", default="", help="The nickname of the study.")
def start(
    strategy_interval: int,
    n_iterations: int,
    lcfr_threshold: int,
    discount_interval: int,
    c: int,
    n_players: int,
    dump_iteration: int,
    update_threshold: int,
    nickname: str,
):
    """Train agent from scratch."""
    # Write config to file, and create directory to save results in.
    config: Dict[str, int] = {**locals()}
    save_path: Path = utils.io.create_dir(nickname)
    with open(save_path / "config.yaml", "w") as steam:
        yaml.dump(config, steam)
    log.info(
        "Only one process specified so using poker_ai.ai.singleprocess."
        "simple_search for the optimisation."
    )
    simple_search(
        config=config,
        save_path=save_path,
        strategy_interval=strategy_interval,
        n_iterations=n_iterations,
        lcfr_threshold=lcfr_threshold,
        discount_interval=discount_interval,
        c=c,
        n_players=n_players,
        dump_iteration=dump_iteration,
        update_threshold=update_threshold,
    )


if __name__ == "__main__":
    train()
