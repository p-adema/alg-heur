from typing import NamedTuple


class Station(NamedTuple):
    """ Class representing a single station """
    name: str
    N: float
    E: float


class StationConnections(dict):
    """ Class representing the connections a station has with other stations """

    def __init__(self, station: Station):
        """
        Create a new StationConnections object for a station
        :param station: The origin station
        """
        super().__init__()
        self.station = station

    def __setitem__(self, station: Station, duration: int):
        """
        Set the duration of a trip to a different station
        :param station: The other station
        :param duration: Duration of trip to other station
        """
        super().__setitem__(station, duration)

    def __getitem__(self, station: Station) -> int:
        """
        Retrieve a trip duration to a different station
        :param station: The other station
        :return: Duration of trip in minutes
        """
        return super().__getitem__(station)

    def __repr__(self) -> str:
        """ Return a representation of the connections as a string """
        return f'StationConnections of {self.station.name}: ' + '{' + \
            ', '.join(f'{station}: {duration} min' for station, duration in self.items()) + '}'


def load(positions_filename: str, connections_filename: str) \
        -> tuple[tuple[Station, ...], dict[Station, StationConnections]]:
    """
    Load the stations and their connections from two files
    :param positions_filename: Filename for the names and coordinates of stations
    :param connections_filename: Filename for the connections between stations
    :return: A tuple of all stations, and a dictionary of trip durations
    """
    stations = []
    names = {}
    with open(positions_filename, 'r') as positions_file:
        positions_file.readline()
        for name, N, E in (line.strip().split(',') for line in positions_file):
            station = Station(name, float(N), float(E))
            stations.append(station)
            names[name] = station

    connections = {station: StationConnections(station) for station in stations}
    with open(connections_filename, 'r') as connections_file:
        connections_file.readline()
        for name_a, name_b, time_str in (line.strip().split(',') for line in connections_file):
            station_a, station_b, time = names[name_a], names[name_b], int(time_str)
            connections[station_a][station_b] = time
            connections[station_b][station_a] = time

    return tuple(stations), connections
