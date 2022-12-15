import EngineMatch
from Engine import Engine

# Function for testing multiple engines against one base engine
def test(testEngineNames: list, baseEngineName: str, games: int, timeLimit: float, processes: int, outputPath: str):
    # Test every engine against the base engine separately
    baseEngine = Engine(baseEngineName, [])
    for testEngineName in testEngineNames:
        # Complete engine match
        testEngine = Engine(testEngineName, [])
        results = EngineMatch.engineMatch([testEngine, baseEngine], games, timeLimit, processes, games)

        # Print out match stats
        statString = results.statString()
        print(statString)
        if outputPath:
            with open(outputPath, "w") as file:
                file.write(statString)