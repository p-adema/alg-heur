""" Classes representing rail infrastructure """

from __future__ import annotations

from typing import NamedTuple


class Station(NamedTuple):
    """ Class representing a single station """
    name: str
    N: float
    E: float

    def __repr__(self):
        """ Returns a short representation of the station """
        return f"Station('{self.name}')"


class Rails:
    """ Class representing the full rail network """

    def __init__(self):
        """ Create an empty network """
        self.stations: tuple[Station, ...] = ()
        self.connections: dict[Station, dict[Station, int]] = {}
        self.names: dict[str, Station] = {}
        self.links = 0

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
        with open(connections_filename, 'r', encoding='utf-8') as connections_file:
            connections_file.readline()
            for name_a, name_b, time_str in (line.strip().split(',') for line in connections_file):
                station_a, station_b = self.names[name_a], self.names[name_b]
                self.connections[station_a][station_b] = int(time_str)
                self.connections[station_b][station_a] = int(time_str)
                self.links += 1

        self.stations = tuple(stations)

    def __getitem__(self, station: Station) -> dict[Station, int]:
        """ Retrieve the connections to other stations, from a given station """
        return self.connections[station]

    def __repr__(self) -> str:
        """ Return a short string summary of the network """
        return f'Rails({len(self.stations)} stations)'
