from __future__ import annotations

import itertools
from collections import deque
from typing import Generator, Any, NamedTuple

from src.classes.rails import Station, Rails


class TrainLineExtension(NamedTuple):
    new: bool
    duration: int
    line: TrainLine
    origin: Station
    destination: Station

    def commit(self) -> bool:
        return self.line.extend(self.origin, self.destination, self.new)

    def __lt__(self, other: TrainLineExtension | Any):
        try:
            if self.new != other.new:
                return self.new < other.new
            return self.duration > other.duration
        except AttributeError:
            return NotImplemented

    def __gt__(self, other: TrainLineExtension | Any):
        try:
            if self.new != other.new:
                return self.new > other.new
            return self.duration < other.duration
        except AttributeError:
            return NotImplemented


class TrainLine:
    def __init__(self, root: Station, rails: Rails, network: Network, max_duration: int):
        self.stations: deque[Station] = deque([root])
        self._rails = rails
        self._network = network
        self.duration = 0
        self.max_duration = max_duration

    def extend(self, origin: Station, destination: Station, is_new: bool = None) -> bool:
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

    def _gen_extensions(self, origin: Station, back: Station = None) \
            -> Generator[TrainLineExtension, None, None]:
        remaining_duration = self.max_duration - self.duration
        for extension, d_duration in self._rails[origin].items():
            if d_duration <= remaining_duration and extension is not back:
                yield TrainLineExtension(
                    extension in self._network.unlinked[origin],
                    d_duration, self, origin, extension)

    def extensions(self) -> list[TrainLineExtension]:
        if len(self.stations) == 1:
            return list(
                self._gen_extensions(self.stations[-1])
            )
        if self.stations[-1] is self.stations[0]:
            return []

        return list(itertools.chain(
            self._gen_extensions(self.stations[-1], self.stations[-2]),
            self._gen_extensions(self.stations[0], self.stations[1])
        ))

    def __repr__(self) -> str:
        return f'TrainLine({len(self.stations)} station(s), {self.duration} min)'

    def output(self) -> str:
        return '"[' + ', '.join(station.name for station in self.stations) + ']"'


class Network:
    def __init__(self, rails: Rails, max_line_duration: int = 120):
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
        line = TrainLine(root, self._rails, self, self._max_line_duration)
        self.lines.append(line)
        return line

    def extensions(self) -> list[TrainLineExtension]:
        return list(itertools.chain.from_iterable(
            line.extensions() for line in self.lines
        ))

    def coverage(self):
        return self.links / self._rails.links

    def fully_covered(self):
        return self.links == self._rails.links

    def total_duration(self) -> int:
        return sum(line.duration for line in self.lines)

    def quality(self) -> float:
        return self.coverage() * 10_000 - (len(self.lines) * 100 + self.total_duration())

    def __repr__(self) -> str:
        return f'Network({len(self.lines)} line(s), {self.coverage():.1%} coverage)'

    def __lt__(self, other: Network | Any):
        try:
            return self.quality() < other.quality()
        except AttributeError:
            return NotImplemented

    def to_output(self) -> str:
        line_outputs = [f'train_{i},{line.output()}\n' for i, line in enumerate(self.lines)]
        return 'train,stations\n' + ''.join(line_outputs) + f'score,{self.quality()}'

    @classmethod
    def from_state(cls, state: NetworkState):
        net = cls(state.infra)
        for out_line in state.lines:
            net_line = net.add_line(out_line[0])
            for s_a, s_b in itertools.pairwise(out_line):
                net_line.extend(s_a, s_b)

        return net

    @classmethod
    def from_output(cls, out: str, infra: Rails) -> Network:
        return cls.from_state(NetworkState.from_output(out, infra))


class NetworkState(NamedTuple):
    lines: tuple[tuple[Station]]
    infra: Rails

    @classmethod
    def from_network(cls, net: Network, infra: Rails) -> NetworkState:
        return cls(tuple(tuple(line.stations) for line in net.lines), infra)

    @classmethod
    def from_output(cls, output: str, infra: Rails) -> NetworkState:
        return cls(tuple(
            tuple(infra.names[name] for name in line) for line in
            (line.split('"')[1][1:-1].split(', ') for line in output.split('\n')[1:-1])
        ), infra)

    def __repr__(self) -> str:
        return f'NetworkState({len(self.lines)} line(s))'

    def __eq__(self, other: NetworkState | Any):
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
