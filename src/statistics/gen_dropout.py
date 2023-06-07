from os.path import isfile

from src.defaults import default_runner as runner, default_infra

PERCENTILE = 90
PRECISION = 3_000

STATION_HEADER = "name,quality\n"


def safety_check(path: str) -> bool:
    if isfile(path):
        print(f'Datafile already present at {path}')
        if input(f"     Overwrite data? (y/N)  ").lower() != 'y':
            print('     Aborted.')
            return False
    return True


def drop_station(dropped: str | None = None) -> float:
    print('Measuring', dropped)
    if dropped is not None:
        infra = default_infra.copy()
        infra.drop_stations(names=[dropped])
        count = PRECISION
    else:
        infra = default_infra
        count = PRECISION * 3
    runner.infra = infra
    return runner.percentile(PERCENTILE, count)


def drop_all_stations() -> None:
    path = f'results/statistics/{runner.name}_drop_stations.csv'
    if not safety_check(path):
        return

    print('Testing all station drops')
    with open(path, 'w') as file:
        file.write(STATION_HEADER)
        file.write(f',{drop_station()}\n')
        for name in default_infra.names.keys():
            file.write(f'{name},{drop_station(name)}\n')


if __name__ == '__main__':
    drop_all_stations()
