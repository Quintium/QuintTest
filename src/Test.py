import time
import EngineMatch
from Engine import Engine
from Results import Results

def test(engineNames: str, games: int, timeLimit: float, processes: int, outputPath: str):
    engines = [Engine(name, []) for name in engineNames]

    start = time.time()
    results = EngineMatch.pairEngines(engines, games, timeLimit, processes, games)
    timePassed = round(time.time() - start, 2)

    statString = results.statString()
    print(statString)
    if outputPath:
        with open(outputPath, "w") as file:
            file.write(statString)