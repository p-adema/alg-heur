from __future__ import annotations

import dataclasses
from collections import deque
from typing import Callable, Generator, Any
from functools import partial
from dataclasses import dataclass
import itertools
from src.classes.rails import Station, Rails


@dataclass(slots=True, frozen=True)
class TrainLineExtension:
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


class TrainLine:
    def __init__(self, root: Station, rails: Rails, network: Network, max_duration: int):
        self.stations: deque[Station] = deque([root])
        self._rails = rails
        self._network = network
        self.duration = 0
        self.max_duration = max_duration

    def extend(self, origin: Station, destination: Station, is_new: bool = None) -> bool:
        if is_new is None:
            is_new = (origin, destination) in self._network.unlinked
        is_end = origin is self.stations[-1]
        is_beginning = origin is self.stations[0]
        if not is_end and not is_beginning:
            print(f'Warning: Disconnected train line extension attempted from {origin.name} to {destination.name}')
            return False
        try:
            ex_duration = self._rails[origin][destination]
        except KeyError:
            print("Warning: there is no rail between origin and destination")
            return False
        if is_new:
            try:
                self._network.unlinked.remove((origin, destination))
                self._network.unlinked.remove((destination, origin))
            except KeyError:
                print("Warning: invalid is_new value passed to TrainLine.extend")
                return False
        else:
            self._network.overtime += ex_duration
        self.duration += ex_duration
        if is_end:
            self.stations.append(destination)
        else:
            self.stations.appendleft(destination)

    def _gen_extensions(self, origin: Station, back: Station = None) \
            -> Generator[TrainLineExtension, None, None]:
        remaining_duration = self.max_duration - self.duration
        for extension, d_duration in self._rails[origin].items():
            if d_duration <= remaining_duration and extension is not back:
                yield TrainLineExtension(
                    (origin, extension) in self._network.unlinked,
                    d_duration, self, origin, extension)

    def extensions(self) -> list[TrainLineExtension]:
        if len(self.stations) == 1:
            return list(
                self._gen_extensions(self.stations[-1])
            )
        elif self.stations[-1] is self.stations[0]:
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
        self.unlinked: set[tuple[Station, Station]] = {
            (stn_a, stn_b)
            for stn_a, stn_conn in rails.connections.items()
            for stn_b in stn_conn
        }
        self.total_links = len(self.unlinked) / 2
        self.overtime = 0
        self._max_line_duration = max_line_duration

    def add_line(self, root: Station) -> TrainLine:
        tl = TrainLine(root, self._rails, self, self._max_line_duration)
        self.lines.append(tl)
        return tl

    def extensions(self) -> list[TrainLineExtension]:
        return list(itertools.chain.from_iterable(
            line.extensions() for line in self.lines
        ))

    def coverage(self):
        return 1 - (len(self.unlinked) / (self.total_links * 2))

    def fully_covered(self):
        return not self.unlinked

    def total_duration(self) -> int:
        return sum(line.duration for line in self.lines)

    def quality(self) -> float:
        return self.coverage() * 10_000 - (len(self.lines) * 100 + self.total_duration())

    def __repr__(self) -> str:
        return f'Network({len(self.lines)} line(s), {self.coverage():.1%} coverage)'

    def __lt__(self, other: Network):
        try:
            return self.quality() < other.quality()
        except AttributeError:
            return NotImplemented

    def output(self) -> str:
        line_outputs = [f'train_{i},{line.output()}\n' for i, line in enumerate(self.lines)]
        return 'train,stations\n' + ''.join(line_outputs) + f'score,{self.quality()}'

    @classmethod
    def from_output(cls, infra: Rails, out: str) -> Network:
        lines = (line.split('"')[1][1:-1].split(', ') for line in out.split('\n')[1:-1])
        net = cls(infra)
        for out_line in lines:
            net_line = net.add_line(infra.names[out_line[0]])
            for s_a, s_b in itertools.pairwise(out_line):
                net_line.extend(infra.names[s_a], infra.names[s_b])

        return net


if __name__ == '__main__':
    r = Rails()
    r.load('data/positions_small.csv', 'data/connections_small.csv')
    n = Network(r)
    line0 = n.add_line(r.stations[0])
