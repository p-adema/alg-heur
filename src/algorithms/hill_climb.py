""" Hill climbing iterative Network generator """
from __future__ import annotations

from src.classes.lines import Network


def next_network(base: Network, max_lines: int = 7) -> Network | None:
    quality = base.quality()
    for state_neighbour in base.state_neighbours(max_lines):
        if state_neighbour.quality() > quality:
            return state_neighbour
