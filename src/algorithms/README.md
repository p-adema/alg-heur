# Algorithms

This folder contains the algorithms implemented for solving the problem

* [standard](standard.py) contains implementations for standard algorithms
    * `Random` is a random constructive algorithm
    * `Greedy` is a simple, greedy, constructive algorithm
    * `HillClimb` is a simple iterative hill climbing algorithm that takes the first good move
    * `LookAhead` is a best-first iterative algorithm that explores future possibilities
    * `SimulatedAnnealing` is an iterative algorithm that transitions from semi-random action to hill climbing
* [generic](generic.py) contains a class for generic constructive algorithms that evaluate heuristics
* [heuristics](heuristics.py) contains heuristics for generic algorithms
* [adjusters](adjusters.py) contains adjusters for heuristic weight distributions