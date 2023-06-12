""" Adjustment functions to run on heuristic outputs """

from math import exp


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
