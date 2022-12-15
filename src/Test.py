import EngineMatch
from Engine import Engine

def test(testEngineNames: list, baseEngineName: str, games: int, timeLimit: float, processes: int, outputPath: str):
    baseEngine = Engine(baseEngineName, [])

    for testEngineName in testEngineNames:
        testEngine = Engine(testEngineName, [])
        results = EngineMatch.engineMatch([testEngine, baseEngine], games, timeLimit, processes, games)

        statString = results.statString()
        print(statString)
        if outputPath:
            with open(outputPath, "w") as file:
                file.write(statString)