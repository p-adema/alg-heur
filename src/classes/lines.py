from __future__ import annotations

import dataclasses
from collections import deque
from typing import Callable, Generator, Any
from functools import partial
from dataclasses import dataclass
import itertools
from src.classes.rails import Station, Rails


@dataclass(slots=True)
class _ExtensionValidity:
    valid: bool = True


@dataclass(slots=True, frozen=True)
class TrainLineExtension:
    new: bool
    duration: int
    line: TrainLine
    origin: Station
    destination: Station
    validity: _ExtensionValidity = dataclasses.field(default_factory=_ExtensionValidity)

    def commit(self) -> bool:
        if self.validity.valid:
            self.validity.valid = False
            return self.line.extend(self.origin, self.destination, self.new)
        print("Warning: double commit attempted (invalid extension)")
        return False

    def __lt__(self, other: TrainLineExtension | Any):
        if not isinstance(other, TrainLineExtension):
            return NotImplemented
        return self.new < other.new or self.duration > other.duration


class TrainLine:
    def __init__(self, root: Station, rails: Rails, network: Network, max_duration: int):
        self.stations: deque[Station] = deque([root])
        self._rails = rails
        self._network = network
        self.duration = 0
        self.max_duration = max_duration

    @property
    def front(self):
        return self.stations[-1]

    @property
    def back(self):
        return self.stations[0]

    def extend(self, origin: Station, destination: Station, is_new: bool = None) -> bool:
        if is_new is None:
            is_new = (origin, destination) in self._network.unlinked

        if origin is self.front:
            self._extend_front(destination, is_new)
            return True
        elif origin is self.back:
            self._extend_back(destination, is_new)
            return True
        print(f'Warning: Disconnected train line extension attempted from {origin.name} to {destination.name}')
        return False

    def _extend_front(self, station: Station, is_new: bool):
        self.duration += self._rails[self.front][station]
        if is_new:
            try:
                self._network.unlinked.remove((self.front, station))
                self._network.unlinked.remove((station, self.front))
            except KeyError:
                print("Warning: invalid is_new value passed to TrainLine.extend")
        else:
            self._network.overlap += 1
        self.stations.append(station)

    def _extend_back(self, station: Station, is_new: bool):
        self.duration += self._rails[self.back][station]
        if is_new:
            try:
                self._network.unlinked.remove((station, self.back))
                self._network.unlinked.remove((self.back, station))
            except KeyError:
                print("Warning: invalid is_new value passed to TrainLine.extend")
        else:
            self._network.overlap += 1
        self.stations.appendleft(station)

    def _gen_extensions(self, origin: Station, back: Station = None) \
            -> Generator[TrainLineExtension, None, None]:
        remaining_duration = self.max_duration - self.duration
        validity = _ExtensionValidity()
        for extension, d_duration in self._rails[origin].items():
            if d_duration <= remaining_duration and extension is not back:
                yield TrainLineExtension(
                    (origin, extension) in self._network.unlinked,
                    d_duration, self, origin, extension, validity)

    def legal_extensions(self) -> list[TrainLineExtension]:
        if len(self.stations) == 1:
            return sorted(
                self._gen_extensions(self.front)
            )
        elif self.front is self.back:
            return []

        return sorted(itertools.chain(
            self._gen_extensions(self.front, self.stations[-2]),
            self._gen_extensions(self.back, self.stations[1])
        ))

    def __repr__(self) -> str:
        return f'TrainLine({len(self.stations)} station(s), {self.duration} min)'


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
        self.overlap = 0
        self._max_line_duration = max_line_duration

    def add_line(self, root: Station) -> TrainLine:
        tl = TrainLine(root, self._rails, self, self._max_line_duration)
        self.lines.append(tl)
        return tl

    def coverage(self):
        return 1 - (len(self.unlinked) / (self.total_links * 2))

    def total_duration(self) -> int:
        return sum(line.duration for line in self.lines)

    def quality(self) -> float:
        return self.coverage() * 10_000 - (len(self.lines) * 100 + self.total_duration())


if __name__ == '__main__':
    r = Rails()
    r.load('data/positions_small.csv', 'data/connections_small.csv')
    n = Network(r)
    line0 = n.add_line(r.stations[0])
