""" Classes representing moves in state space (network modifications) """

from __future__ import annotations

from typing import NamedTuple, TYPE_CHECKING

if TYPE_CHECKING:
    # Prevent import loop
    from src.classes.lines import Network, TrainLine
    from src.classes.rails import Station


class ExtensionMove(NamedTuple):
    """ Represents an extension of one vertex to a train line """
    new: bool
    duration: int
    line: TrainLine
    origin: Station
    destination: Station

    def commit(self) -> bool:
        """ Confirm this extension, adding the destination to the line """
        return self.line.extend(self.origin, self.destination, self.new)

    def rebind(self, net: Network) -> ExtensionMove:
        """ Rebind this extension to the corresponding line in 'net' """
        return self._replace(line=net.lines[self.line.index])


class RetractionMove(NamedTuple):
    """ Represents a retraction of one vertex to a train line """
    from_end: bool
    line: TrainLine

    def commit(self) -> bool:
        """ Confirm this retraction, removing a station from the line """
        return self.line.retract(self.from_end)

    def rebind(self, net: Network) -> RetractionMove:
        """ Rebind this retraction to the corresponding line in 'net' """
        return self._replace(line=net.lines[self.line.index])

    def evident(self) -> bool:
        """ Checks whether this retraction is a retraction over an overlap """
        if self.from_end:
            last, rem = self.line.stations[-1], self.line.stations[-2]
        else:
            last, rem = self.line.stations[0], self.line.stations[1]
        return bool(self.line.network.link_count[last][rem] - 1)


class RemovalMove(NamedTuple):
    """ Represents a removal of a train line """
    index: int
    network: Network

    def commit(self) -> bool:
        """ Confirm this removal, removing a line from the network """
        del self.network.lines[self.index]
        for line in self.network.lines[self.index:]:
            line.index -= 1
        return True

    def rebind(self, net: Network):
        """ Rebind this removal to a different network """
        return self._replace(network=net)


class AdditionMove(NamedTuple):
    """ Represents an addition of a train line """
    root: Station
    network: Network

    def commit(self) -> bool:
        """ Confirm this addition, adding a train line """
        self.network.add_line(self.root)
        return True

    def rebind(self, net: Network) -> AdditionMove:
        """ Rebind this addition to a different network """
        return self._replace(network=net)

    def degree(self) -> int:
        """ The amount of free connections the root of this addition has """
        return self.network.free_degree[self.root]


if TYPE_CHECKING:
    # Pylint doesn't see NamedTuple._replace
    # See: https://github.com/pylint-dev/pylint/issues/4070
    def _replace(self, **_):
        return self


    ExtensionMove._replace = _replace
    RetractionMove._replace = _replace
    RemovalMove._replace = _replace
    AdditionMove._replace = _replace
