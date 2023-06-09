""" Base type definitions for various types and objects """

from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Protocol, TypeAlias, Callable

from src.classes.lines import Network


class Algorithm(ABC):
    """ Base class for all Algorithm types """

    # Lowercase identifier for algorithms
    name: str = 'ba'

    def __init__(self, base: Network, **options):
        self.active = base
        self.options = options

    def __iter__(self):
        return self

    @abstractmethod
    def __next__(self) -> Network: ...


class Move(Protocol):
    """ Represents a possible move in state space """

    @abstractmethod
    def commit(self) -> bool:
        """ Commit this move """

    @abstractmethod
    def rebind(self, net: Network) -> Move:
        """ Rebind this move to the given network """


# (CurrentNetwork, NextMove) -> Evaluation
Heuristic: TypeAlias = Callable[[Network, Move], float]

# (Evaluations) -> AdjustedEvaluations
Adjuster: TypeAlias = Callable[[list[float]], list[float]]
