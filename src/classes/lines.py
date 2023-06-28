""" Classes representing a train line network """
from __future__ import annotations

import itertools
from collections import deque
from copy import copy
from typing import Generator, Any, NamedTuple, Iterator, TYPE_CHECKING

from src.classes.moves import ExtensionMove, RetractionMove, RemovalMove, AdditionMove
from src.classes.rails import Station, Rails

if TYPE_CHECKING:
    from src.classes.abstract import Move


class TrainLine:
    """ Class representing a train line """

    def __init__(self, root: Station, network: Network, dist_cap: int, location: int):
        """
        Create a new TrainLine
        :param root: The origin station of the line
        :param network: The network the line belongs to
        :param dist_cap: The maximum duration of the line
        :param location: The index of the line in the network
        """
        self.stations: deque[Station] = deque([root])
        self.rails = network.rails
        self.network: Network = network
        self.duration = 0
        self.dist_cap = dist_cap
        self.location: int = location

    def extend(self, origin: Station, destination: Station, is_new: bool | None = None) -> bool:
        """
        Add a station to the line
        :param origin: Station to extend from, must be head or tail of line
        :param destination: Station to extend to
        :param is_new: If known, whether this extension is new to the network
        :return: False on error
        """
        if is_new is None:
            is_new = not self.network.link_count[origin][destination]
        is_end = origin is self.stations[-1]
        is_beginning = origin is self.stations[0]
        if not is_end and not is_beginning:
            print('Warning: Disconnected train line extension attempted')
            return False
        try:
            ex_duration = self.rails[origin][destination]
        except KeyError:
            print("Warning: there is no rail between origin and destination")
            return False
        self.network.link_count[origin][destination] += 1
        self.network.link_count[destination][origin] += 1
        if is_new:
            self.network.total_links += 1
            self.network.free_degree[origin] -= 1
            self.network.free_degree[destination] -= 1
        else:
            self.network.overtime += ex_duration
        self.duration += ex_duration
        if is_end:
            self.stations.append(destination)
        else:
            self.stations.appendleft(destination)
        return True

    def retract(self, from_end: bool, is_last: bool | None = None) -> bool:
        """
        Remove a station from an end
        :param from_end: Whether to remove from the end or the beginning of the line
        :param is_last: If known, whether this removal would change network coverage
        :return: False on error
        """
        removed = self.stations.pop() if from_end else self.stations.popleft()
        remaining = self.stations[-1] if from_end else self.stations[0]
        try:
            rem_duration = self.rails[remaining][removed]
            self.network.link_count[remaining][removed] -= 1
            self.network.link_count[removed][remaining] -= 1
        except KeyError:
            print("Warning: TrainLine improperly constructed")
            return False
        self.duration -= rem_duration
        if is_last is None:
            is_last = not self.network.link_count[remaining][removed]

        if is_last:
            self.network.total_links -= 1
            self.network.free_degree[remaining] += 1
            self.network.free_degree[removed] += 1
        else:
            self.network.overtime -= rem_duration
        return True

    def gen_extensions(self, origin: Station,
                       back: Station | None = None) -> Generator[ExtensionMove]:
        """
        Generate individual extensions from this line
        :param origin: Either the head or tail of the line
        :param back: Previous station in line, to prevent backtracking
        :return: Yields ExtensionMoves
        """
        remaining_duration = self.dist_cap - self.duration
        for extension, d_duration in self.rails[origin].items():
            if d_duration <= remaining_duration and extension is not back:
                yield ExtensionMove(
                    not self.network.link_count[origin][extension],
                    d_duration, self, origin, extension)

    def extensions(self) -> Iterator[ExtensionMove]:
        """ Get an iterable of all valid extensions to the line """
        if len(self.stations) == 1:
            return self.gen_extensions(self.stations[-1])

        if self.stations[-1] is self.stations[0]:
            return iter(())

        return itertools.chain(
            self.gen_extensions(self.stations[-1], self.stations[-2]),
            self.gen_extensions(self.stations[0], self.stations[1])
        )

    def retractions(self) -> Iterator[RetractionMove]:
        """ Get an iterator of all valid retractions from this line """
        if len(self.stations) == 1:
            return iter(())

        if len(self.stations) == 2:
            return iter((RetractionMove(True, self),))
        return iter((
            RetractionMove(False, self),
            RetractionMove(True, self))
        )

    def __repr__(self) -> str:
        """ Represent the train line in a short format """
        return f"TrainLine({len(self.stations)} station{'' if len(self.stations) == 1 else 's'}," \
               f" {self.duration} min)"

    def output(self) -> str:
        """ Turn the train line into the format required for A&H output files """
        return '"[' + ', '.join(station.name for station in self.stations) + ']"'

    def copy(self, net: Network) -> TrainLine:
        """ Create a copy of this train line, onto the given network """
        new = TrainLine(self.stations[0], net, self.dist_cap, self.location)
        new.stations = copy(self.stations)
        new.duration = self.duration
        return new


class Network:
    """ A class representing a network of train lines """

    def __init__(self, rails: Rails, dist_cap: int = 120):
        """
        Create a new network
        :param rails: The infrastructure the network is build on
        :param dist_cap: The maximum runtime of any single line
        """
        self.rails = rails
        self._dist_cap = dist_cap
        self.lines: list[TrainLine] = []
        self.link_count: dict[Station, dict[Station, int]] = {}
        self.free_degree: dict[Station, int] = {}

        for stn_a, stn_conn in rails.connections.items():
            self.link_count[stn_a] = {stn_b: 0 for stn_b in stn_conn.keys()}
            self.free_degree[stn_a] = len(stn_conn)

        self.total_links = 0
        self.overtime = 0

    def add_line(self, root: Station) -> TrainLine:
        """ Add a new line, starting from the root station """
        line = TrainLine(root, self, self._dist_cap, len(self.lines))
        self.lines.append(line)
        return line

    def extensions(self) -> Iterator[ExtensionMove]:
        """ Get an iterator of all possible extensions to all train lines """
        return itertools.chain.from_iterable(
            line.extensions() for line in self.lines
        )

    def retractions(self) -> Iterator[RetractionMove]:
        """ Get an iterator of all possible retractions to all train lines """
        return itertools.chain.from_iterable(
            line.retractions() for line in self.lines
        )

    def removals(self) -> Iterator[RemovalMove]:
        """ Get an iterator of all possible line removals """
        return (RemovalMove(line.location, self)
                for line in self.lines if len(line.stations) == 1)

    def additions(self) -> Iterator[AdditionMove]:
        """ Get an iterator of all possible line additions """
        return (AdditionMove(station, self) for station, free
                in self.free_degree.items() if free)

    def moves(self, addition: bool = True) -> Iterator[Move]:
        """ Get an iterator of all possible moves """
        standard: itertools.chain[Move] = itertools.chain(
            self.extensions(),
            self.retractions(),
            self.removals()
        )
        if addition:
            return itertools.chain(standard, self.additions())
        return standard

    def constructions(self, addition: bool = True) -> Iterator[Move]:
        """ Get an iterator of all constructive moves """
        if not addition:
            return self.extensions()
        return itertools.chain(self.extensions(), self.additions())

    def trim(self):
        """ Remove plainly useless rails (overlaps at ends) """
        act = True
        while act:
            act = False
            for ret in self.retractions():
                if ret.evident():
                    ret.commit()
                    act = True

    def coverage(self):
        """ The fraction of the rails covered """
        return self.total_links / self.rails.links

    def fully_covered(self):
        """ Whether the network covers all rails """
        return self.total_links == self.rails.links

    def total_duration(self) -> int:
        """ Total duration of lines in the network """
        return sum(line.duration for line in self.lines)

    def quality(self) -> float:
        """
        Quality score, as given by the case description:
            Q = coverage * 10_000 - (lines * 100 + total_duration)
        """
        return self.coverage() * 10_000 - (len(self.lines) * 100 + self.total_duration())

    def is_optimal(self) -> bool:
        """ Whether this network, given a constant rail count, is optimal """
        return not self.overtime and self.fully_covered()

    def __repr__(self) -> str:
        """ Represent the network in a short format """
        return f"Network({len(self.lines)} line{'' if len(self.lines) == 1 else 's'}," \
               f" {self.coverage():.1%} coverage)"

    def __lt__(self, other: Network | Any):
        """ Whether this network has a lower quality than other """
        try:
            return self.quality() < other.quality()
        except AttributeError:
            return NotImplemented

    def __gt__(self, other: Network | Any):
        """ Whether this network has a lower quality than other """
        try:
            return self.quality() > other.quality()
        except AttributeError:
            return NotImplemented

    def to_output(self) -> str:
        """ Generate an output string in the format required by A&H output files """
        line_outputs = [f'train_{i},{line.output()}\n' for i, line in enumerate(self.lines)]
        return 'train,stations\n' + ''.join(line_outputs) + f'score,{self.quality()}'

    @classmethod
    def from_state(cls, state: NetworkState):
        """ Create a Network from a NetworkState """
        net = cls(state.infra)
        for out_line in state.lines:
            net_line = net.add_line(out_line[0])
            for s_a, s_b in itertools.pairwise(out_line):
                net_line.extend(s_a, s_b)

        return net

    @classmethod
    def from_output(cls, out: str, infra: Rails) -> Network:
        """ Create a Network from an output string, on given infrastructure """
        return cls.from_state(NetworkState.from_output(out, infra))

    def copy(self) -> Network:
        """ Create a copy of this network """
        net = Network(self.rails, self._dist_cap)
        net.lines = [line.copy(net) for line in self.lines]
        net.link_count = {
            stn_a: copy(stn_conn)
            for stn_a, stn_conn in self.link_count.items()
        }
        net.total_links = self.total_links
        net.overtime = self.overtime
        return net

    def pivot(self) -> Generator[Network]:
        """ Repeatedly yield copies of this network """
        while True:
            yield self.copy()

    def state_neighbours(self, line_cap: int, stationary: bool = False,
                         constructive: bool = False) -> Generator[Network]:
        """ Yield all state neighbours from this network, including
            this network if stationary is True,
            without retractions if constructive is true             """
        addition = len(self.lines) < line_cap
        if not constructive:
            moves = self.moves(addition)
        else:
            moves = self.constructions(addition)
        for move, net in zip(moves, self.pivot()):
            move.rebind(net).commit()
            net.move = move
            yield net
        if stationary:
            yield self.copy()


class NetworkState(NamedTuple):
    """ A class compactly representing a single state of a network """
    lines: tuple[tuple[Station, ...], ...]
    infra: Rails
    score: float

    @classmethod
    def from_network(cls, net: Network) -> NetworkState:
        """ Create a NetworkState from a network """
        return cls(tuple(tuple(line.stations) for line in net.lines), net.rails, net.quality())

    @classmethod
    def from_output(cls, output: str, infra: Rails) -> NetworkState:
        """ Create a NetworkState from an output string and on given infrastructure """
        return cls(tuple(
            tuple(infra.names[name] for name in line) for line in
            (line.split('"')[1][1:-1].split(', ') for line in output.split('\n')[1:-1])
        ), infra, float(output.split('score,')[1]))

    def __repr__(self) -> str:
        """ Represent a NetworkState in a short format """
        return f"NetworkState({len(self.lines)} line{'' if len(self.lines) == 1 else 's'})"

    def __eq__(self, other: NetworkState | Any):
        """ Whether two NetworkStates are equivalent """
        if not isinstance(other, NetworkState):
            return False

        if self.infra is not other.infra or len(self.lines) != len(other.lines):
            return False

        indices = list(range(len(self.lines)))

        for line in self.lines:
            equiv = False
            for i in indices:
                if line == other.lines[i] or line == tuple(reversed(other.lines[i])):
                    indices.remove(i)
                    equiv = True
                    break
            if not equiv:
                return False

        return not indices


if __name__ == '__main__':
    r = Rails()
    r.load('data/positions.csv', 'data/connections.csv')
    n = Network(r)
    line0 = n.add_line(r.stations[0])
