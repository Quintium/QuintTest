import EngineMatch
from Engine import Engine

def test(engineNames: str, games: int, timeLimit: float, processes: int, outputPath: str):
    engines = [Engine(name, []) for name in engineNames]
    results = EngineMatch.engineMatch(engines, games, timeLimit, processes, games)

    statString = results.statString()
    print(statString)
    if outputPath:
        with open(outputPath, "w") as file:
            file.write(statString)