""" Classes representing rail infrastructure """

from __future__ import annotations

import math
import random
from typing import NamedTuple, Generator, Literal


class Station(NamedTuple):
    """ Class representing a single station """
    name: str
    N: float
    E: float

    def __repr__(self):
        """ Returns a short representation of the station """
        return f"Station('{self.name}')"

    def distance(self, other: Station):
        """ Returns the Euclidian distance to another station in degrees """
        return math.sqrt((self.N - other.N) ** 2 + (self.E - other.E) ** 2)


class RailModification(NamedTuple):
    """ Wrapper for a modification to the rail network """
    type: Literal['move_rail'] | Literal['drop_rail'] \
          | Literal['add_rail'] | Literal['drop_station']
    origin: Station
    dest: Station | None = None


class Rails:
    """ Class representing the full rail network """

    def __init__(self):
        """ Create an empty network """
        self.stations: tuple[Station, ...] = ()
        self.connections: dict[Station, dict[Station, int]] = {}
        self.names: dict[str, Station] = {}
        self.links = 0

        # max_duration is *not* updated when rails are modified:
        #   it serves as an upper bound to rail length
        self.min_max = [math.inf, -math.inf]

        self.speed: float = -1
        self.modifications: list[RailModification] = []

    def load(self, positions_filename: str, connections_filename: str):
        """
        Load the rail network from a position and a connection file
        :param positions_filename: Filename for the names and coordinates of stations
        :param connections_filename: Filename for the connections between stations
        """
        stations = []
        with open(positions_filename, 'r', encoding='utf-8') as positions_file:
            positions_file.readline()
            for name, n_coord, e_coord in (line.strip().split(',') for line in positions_file):
                station = Station(name, float(n_coord), float(e_coord))
                stations.append(station)
                self.names[name] = station

        self.connections = {station: {} for station in stations}
        sum_speed = 0
        with open(connections_filename, 'r', encoding='utf-8') as connections_file:
            connections_file.readline()
            for station_a, station_b, duration in \
                    ((self.names[name_a], self.names[name_b], int(dur_s))
                     for name_a, name_b, dur_s in
                     (line.strip().split(',') for line in connections_file)):
                self.connections[station_a][station_b] = duration
                self.connections[station_b][station_a] = duration
                self.links += 1
                sum_speed += self._calc_speed(station_a, station_b, duration)
                self.min_max[0] = min(self.min_max[0], duration)
                self.min_max[1] = max(self.min_max[1], duration)

        self.stations = tuple(stations)
        self.speed = sum_speed / self.links

    def copy(self) -> Rails:
        """ Creates a copy of this rail network, for modification """
        new = Rails()
        new.stations = self.stations
        new.connections = {s: c.copy() for s, c in self.connections.items()}
        new.names = self.names
        new.links = self.links
        new.min_max = self.min_max
        new.speed = self.speed
        return new

    def pivot(self) -> Generator[Rails]:
        """ Yields copies of this rail network """
        while True:
            yield self.copy()

    def swap_rails(self, count: int = 3,
                   pairs: list[tuple[str, str]] | None = None):
        """ Swap the destination of 'count' rails randomly,
            estimating the resulting durations from the average speed,
            or do so for specific rails between given station names     """
        if pairs is not None:
            for name_a, name_b in pairs:
                self._swap_rail(self.names[name_a], self.names[name_b])
            return

        for _ in range(count):
            origin = random.choice(self.stations)
            old_outgoing = list(self.connections[origin].keys())
            old_dest = random.choice(old_outgoing)
            self._swap_rail(origin, old_dest)

    def _swap_rail(self, origin: Station, old_dest: Station):
        new_dest = random.choice([dest for dest in self.stations
                                  if dest not in self.connections[origin]
                                  and dest is not origin])
        duration = self._est_time(origin, new_dest)
        del self.connections[origin][old_dest]
        del self.connections[old_dest][origin]
        self.connections[origin][new_dest] = duration
        self.connections[new_dest][origin] = duration
        self.modifications.append(
            RailModification('move_rail', origin, new_dest))

    def add_rails(self, count: int = 3,
                  pairs: list[tuple[str, str]] | None = None):
        """ Add 'count' random rails to the network,
            or specific rails by station names          """
        if pairs is not None:
            for name_a, name_b in pairs:
                self._add_rail(self.names[name_a], self.names[name_b])
            return

        for _ in range(count):
            origin = random.choice(self.stations)
            for station in random.sample(self.stations, len(self.stations)):
                if station is not origin and station not in self.connections[origin]:
                    self._add_rail(origin, station)
                    break

    def _add_rail(self, origin: Station, dest: Station):
        duration = max(self._est_time(origin, dest), 3)
        self.connections[origin][dest] = duration
        self.connections[dest][origin] = duration
        self.links += 1
        self.modifications.append(
            RailModification('add_rail', origin, dest))

    def drop_rails(self, count: int = 3,
                   pairs: list[tuple[str, str]] | None = None):
        """ Drop 'count' random rails from the network,
            or specific rails by station names          """
        if pairs is not None:
            for name_a, name_b in pairs:
                self._drop_rail(self.names[name_a], self.names[name_b])
            return

        for _ in range(count):
            origin = random.choice(self.stations)
            dest = random.choice(list(self.connections[origin].keys()))
            self._drop_rail(origin, dest)

    def _drop_rail(self, origin, dest):
        del self.connections[origin][dest]
        del self.connections[dest][origin]
        self.links -= 1

        if not self.connections[origin]:
            self.stations = tuple(s for s in self.stations if s is not origin)

        if not self.connections[dest]:
            self.stations = tuple(s for s in self.stations if s is not dest)
        self.modifications.append(
            RailModification('drop_rail', origin, dest))

    def drop_stations(self, count: int = 1, names: list[str] | None = None):
        """ Drop 'count' random stations from the network,
            or specific stations by name                    """
        if names is not None:
            for name in names:
                self._drop_station(self.names[name])
            return

        for _ in range(count):
            origin = random.choice(self.stations)
            self._drop_station(origin)

    def _drop_station(self, origin):
        self.stations = tuple(s for s in self.stations if s is not origin)
        self.links -= len(self.connections[origin].keys())
        del self.connections[origin]
        for conn in self.connections.values():
            if origin in conn:
                del conn[origin]
        self.modifications.append(
            RailModification('drop_station', origin))

    @staticmethod
    def _calc_speed(s_a: Station, s_b: Station, time: int) -> float:
        """ Calculate the mean speed (degrees per minute) of a connection """
        return s_a.distance(s_b) / time

    def _est_time(self, s_a: Station, s_b: Station) -> int:
        """ Estimate the duration of a new line based on average speeds """
        return round(self.speed / s_a.distance(s_b))

    def __getitem__(self, station: Station) -> dict[Station, int]:
        """ Retrieve the connections to other stations, from a given station """
        return self.connections[station]

    def __repr__(self) -> str:
        """ Return a short string summary of the network """
        return f'Rails({len(self.stations)} stations)'
