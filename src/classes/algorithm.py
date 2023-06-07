""" ABC for all Algorithms types """

from __future__ import annotations

import abc

from src.classes.lines import Network


class Algorithm(abc.ABC):
    """ Base class for all Algorithm types """
    name: str = 'base'

    def __init__(self, base: Network, **options):
        self.active = base
        self.options = options

    def __iter__(self):
        return self

    @abc.abstractmethod
    def __next__(self) -> Network: ...
