from __future__ import annotations

import random
from typing import Generator

from src.classes.rails import Rails
from src.classes.lines import Network, TrainLineExtension


def gen_extensions(infra: Rails, net: Network, max_lines: int = 7, optimal: bool = False,
                   temperature: float = 0) -> Generator[TrainLineExtension, None, None]:
    net.add_line(random.choice(infra.stations))
    line_count = 1
    while True:
        ext = net.extensions()
        if not ext:
            if line_count == max_lines:
                return
            net.add_line(random.choice(infra.stations))
            line_count += 1
            continue

        if temperature and random.random() < temperature:
            yield ext[0]

        choice = max(ext)
        if choice.new:
            yield choice
        elif line_count < max_lines:
            stations = list(infra.stations)
            random.shuffle(stations)
            for station in stations:
                if net.unlinked[station]:
                    net.add_line(station)
                    line_count += 1
                    break

        elif not optimal:
            yield choice
        else:
            return
