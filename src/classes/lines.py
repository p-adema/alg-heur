""" Classes representing a train line network """

from __future__ import annotations

import itertools
from collections import deque
from typing import Generator, Any, NamedTuple

from src.classes.rails import Station, Rails


class TrainLineExtension(NamedTuple):
    """ Represents an extension of one vertex to a train line """
    new: bool
    duration: int
    line: TrainLine
    origin: Station
    destination: Station

    # _network: Network
    # @property
    # def new(self) -> bool:
    #     """ Whether this track is new to the network """
    #     return self.destination in self._network.unlinked[self.origin]

    def commit(self) -> bool:
        """ Confirm this extension, adding the destination to the line """
        return self.line.extend(self.origin, self.destination, self.new)

    def __lt__(self, other: TrainLineExtension | Any) -> bool:
        """
        Whether this extension is less valuable than other
        New extensions are more valuable, then shorter extensions
        """
        try:
            s_new, o_new = self.new, other.new
            if s_new != o_new:
                return s_new < o_new
            return self.duration > other.duration
        except AttributeError:
            return NotImplemented

    def __gt__(self, other: TrainLineExtension | Any) -> bool:
        """
        Whether this extension is more valuable than other
        New extensions are more valuable, then shorter extensions
        """
        try:
            if self.new != other.new:
                return self.new > other.new
            return self.duration < other.duration
        except AttributeError:
            return NotImplemented


class TrainLine:
    """ Class representing a train line """
    def __init__(self, root: Station, rails: Rails, network: Network, max_duration: int):
        """
        Create a new TrainLine
        :param root: The origin station of the line
        :param rails: The infrastructure the line runs on
        :param network: The network the line belongs to
        :param max_duration: The maximum duration of the line
        """
        self.stations: deque[Station] = deque([root])
        self._rails = rails
        self._network = network
        self.duration = 0
        self.max_duration = max_duration

    def extend(self, origin: Station, destination: Station, is_new: bool = None) -> bool:
        """
        Add a station to the line
        :param origin: Station to extend from, must be head or tail of line
        :param destination: Station to extend to
        :param is_new: If known, whether this extension is new to the network
        :return: False on error
        """
        if is_new is None:
            is_new = destination in self._network.unlinked[origin]
        is_end = origin is self.stations[-1]
        is_beginning = origin is self.stations[0]
        if not is_end and not is_beginning:
            print('Warning: Disconnected train line extension attempted')
            return False
        try:
            ex_duration = self._rails[origin][destination]
        except KeyError:
            print("Warning: there is no rail between origin and destination")
            return False
        if is_new:
            try:
                self._network.unlinked[origin].remove(destination)
                self._network.unlinked[destination].remove(origin)
                self._network.links += 1
            except ValueError:
                print("Warning: invalid is_new value passed to TrainLine.extend")
                return False
        else:
            self._network.overtime += ex_duration
        self.duration += ex_duration
        if is_end:
            self.stations.append(destination)
        else:
            self.stations.appendleft(destination)
        return True

    def gen_extensions(self, origin: Station, back: Station = None) \
            -> Generator[TrainLineExtension]:
        """
        Generate individual extensions from this line
        :param origin: Either the head or tail of the line
        :param back: Previous station in line, to prevent backtracking
        :return: Yields TrainLineExtensions
        """
        remaining_duration = self.max_duration - self.duration
        for extension, d_duration in self._rails[origin].items():
            if d_duration <= remaining_duration and extension is not back:
                yield TrainLineExtension(
                    extension in self._network.unlinked[origin],
                    d_duration, self, origin, extension)

    def extensions(self) -> list[TrainLineExtension]:
        """ Get a list of all valid extensions to the line """
        if len(self.stations) == 1:
            return list(
                self.gen_extensions(self.stations[-1])
            )
        if self.stations[-1] is self.stations[0]:
            return []

        return list(itertools.chain(
            self.gen_extensions(self.stations[-1], self.stations[-2]),
            self.gen_extensions(self.stations[0], self.stations[1])
        ))

    def __repr__(self) -> str:
        """ Represent the train line in a short format """
        return f"TrainLine({len(self.stations)} station{'' if len(self.stations) == 1 else 's'}," \
               f" {self.duration} min)"

    def output(self) -> str:
        """ Turn the train line into the format required for A&H output files """
        return '"[' + ', '.join(station.name for station in self.stations) + ']"'


class Network:
    """ A class representing a network of train lines """
    def __init__(self, rails: Rails, max_line_duration: int = 120):
        """
        Create a new network
        :param rails: The infrastructure the network is build on
        :param max_line_duration: The maximum runtime of any single line
        """
        self._rails = rails
        self.lines: list[TrainLine] = []
        self.unlinked: dict[Station, list[Station]] = {
            stn_a: list(stn_conn.keys())
            for stn_a, stn_conn in rails.connections.items()
        }
        self.links = 0
        self.overtime = 0
        self._max_line_duration = max_line_duration

    def add_line(self, root: Station) -> TrainLine:
        """ Add a new line, starting from the root station """
        line = TrainLine(root, self._rails, self, self._max_line_duration)
        self.lines.append(line)
        return line

    def extensions(self) -> list[TrainLineExtension]:
        """ Get a list of all possible extensions to all train lines """
        return list(itertools.chain.from_iterable(
            line.extensions() for line in self.lines
        ))

    def coverage(self):
        """ The fraction of the rails covered """
        return self.links / self._rails.links

    def fully_covered(self):
        """ Whether the network covers all rails """
        return self.links == self._rails.links

    def total_duration(self) -> int:
        """ Total duration of lines in the network """
        return sum(line.duration for line in self.lines)

    def quality(self) -> float:
        """
        Quality score, as given by the case description:
            Q = coverage * 10_000 - (lines * 100 + total_duration)
        """
        return self.coverage() * 10_000 - (len(self.lines) * 100 + self.total_duration())

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


class NetworkState(NamedTuple):
    """ A class compactly representing a single state of a network """
    lines: tuple[tuple[Station]]
    infra: Rails

    @classmethod
    def from_network(cls, net: Network, infra: Rails) -> NetworkState:
        """ Create a NetworkState from a network and on given infrastructure """
        return cls(tuple(tuple(line.stations) for line in net.lines), infra)

    @classmethod
    def from_output(cls, output: str, infra: Rails) -> NetworkState:
        """ Create a NetworkState from an output string and on given infrastructure """
        return cls(tuple(
            tuple(infra.names[name] for name in line) for line in
            (line.split('"')[1][1:-1].split(', ') for line in output.split('\n')[1:-1])
        ), infra)

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
