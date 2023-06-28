# Railroad optimiser

![](docs/nl_infra.png "NL problem infrastructure")

In the Netherlands, a great deal of infrastructure has been built to allow Intercity trains to cross from one side of
the country to the other. Determining where these trains should run is, however, a challenging task. Networks should try
to cover as much of the built infrastructure as possible while minimising the total duration and the number of distinct
lines. To tackle this problem, I wrote some simple algorithms and heuristics that can approximate a good solution
rapidly and approach an optimal one with sufficient time.

## Getting started

The codebase was written in Python 3.10 but is compatible with Python 3.6+. Installation of the required packages can be
done via the requirements file:

`python -m pip install -r requirements.txt`

## Structure

The repository is divided into four main folders:

* [data](data) - CSV files describing the problem
* [src](src) - Source code for the implementation
* [docs](docs) - Images for this README
* [results](results) - Folder where all results are saved

## Testing

To produce a map for a single run of the default runner, simply execute
`python main.py`

## Graph replication

If you have too much free time, you can replicate the graphs I presented:

To replicate the distributions seen in the presentation, edit the `default_runner` variable
in [the defaults file](src/defaults.py) (set it equal to one of the other Runner variables, 
for example `std_gr` for the standard Greedy implementation)
to the appropriate run configuration, generate distributional data with

`python -m src.statistics.gen_dist`,

enable the desired distributions by uncommenting them in the head of [the graph file](src/graphs/distributions.py) and then show the
graph with

`python -m src.graphs.distributions`

To replicate the graphs of the experiment, set `default_runner` in [the defaults file](src/defaults.py) to the `cst_nf`
Runner, then execute

`python -m src.statistics.gen_experiment`

and

`python -m src.graphs.experiment`

If you have a fancy computer, you can increase the number of processes used
in [the setup file](src/statistics/mp_setup.py)

## Author

Peter Adema (me)

## Acknowledgements

* UvA Minor Programming, for giving me this interesting assignment
* Wouter and Martijn from the minor for helping me participate
* Quinten from the minor, for giving me valuable clarifications on the assignment