from __future__ import annotations

import random
from typing import Generator

from src.classes import rails, lines


def gen_extensions(infra: rails.Rails, net: lines.Network, max_lines: int = 7, optimal: bool = False) \
        -> Generator[lines.TrainLineExtension, None, None]:
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

        choice = max(ext)
        if choice.new:
            yield choice
        elif line_count < max_lines:
            net.add_line(random.choice(infra.stations))
            line_count += 1
        elif not optimal:
            yield choice
        else:
            return
