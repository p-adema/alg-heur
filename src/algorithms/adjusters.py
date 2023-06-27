""" Adjustment functions to run on heuristic outputs """

from heapq import nlargest
from math import exp

from src.classes.abstract import Adjuster


def relu(weights: list[float]) -> list[float]:
    """ Makes no adjustments """
    return [max(0., w) for w in weights]


def argmax(weights: list[float]) -> list[float]:
    """ Concentrates all probability into the highest weight """
    best = max(weights)
    return [(1 if w == best else 0) for w in weights]


def softmax(weights: list[float]) -> list[float]:
    """ Performs a softmax on the weights """
    e_w = [exp(w) for w in weights]
    s_w = sum(e_w)
    return [e / s_w for e in e_w]


def soft_n(top_n: int) -> Adjuster:
    """ Performs a softmax on the top n choices """

    def _soft_n(weights: list[float]) -> list[float]:
        """ Actual adjuster function to perform softmax """
        top = nlargest(top_n + 1, weights)
        low = min(top)
        high = max(top)
        if low == high or high > low + 200:
            # Argmax if we can't reduce
            return [(1 if w == high else 0) for w in weights]
        return softmax(relu([w - low for w in weights]))

    return _soft_n
