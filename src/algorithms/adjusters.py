""" Adjustment functions to run on heuristic outputs """

from heapq import nlargest
from math import exp

from src.classes.abstract import Adjuster


def relu(weights: list[float]) -> list[float]:
    """ Makes all weights zero or positive """
    return [max(0., w) for w in weights]


def argmax(weights: list[float]) -> list[float]:
    """ Concentrates all probability into the highest weight """
    best = max(weights)
    return [(1 if w == best else 0) for w in weights]


def softmax(weights: list[float]) -> list[float]:
    """ Performs a softmax on the weights """
    exp_weights = [exp(w) for w in weights]
    sum_exp = sum(exp_weights)
    return [e / sum_exp for e in exp_weights]


def soft_n(top_n: int) -> Adjuster:
    """ Create an adjuster that
        performs a softmax preferring the top n choices """

    def _soft_n(weights: list[float]) -> list[float]:
        """ Performs a softmax preferring the top n choices """
        top = nlargest(top_n + 1, weights)
        low = min(top)
        high = max(top)
        if low == high or high > low + 200:
            # Argmax if we can't reduce due to similar scores or math domain
            return [(1 if w == high else 0) for w in weights]
        return softmax(relu([w - low for w in weights]))

    return _soft_n
