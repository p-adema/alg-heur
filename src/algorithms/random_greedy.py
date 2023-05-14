from __future__ import annotations

import random
from typing import Generator

from src.classes import rails, lines


def gen_extensions(infra: rails.Rails, net: lines.Network, max_lines: int = 7) \
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
        if choice.new or random.random() < line_count / max_lines:
            yield choice
        else:
            net.add_line(random.choice(infra.stations))
            line_count += 1
