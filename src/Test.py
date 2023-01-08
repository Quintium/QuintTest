import src.EngineMatch
from src.Engine import Engine
from src.TimeControl import TimeControl

# Function for testing multiple engines against one base engine
def test(testEngineNames: list, baseEngineName: str, games: int, timeControl: str, processes: int, outputName: str):
    # Parse time control string
    timeControl = TimeControl(timeControl)

    # Save output string
    outputString = ""

    # Test every engine against the base engine separately
    baseEngine = Engine(baseEngineName, [])
    for testEngineName in testEngineNames:
        # Complete engine match
        testEngine = Engine(testEngineName, [])
        results = src.EngineMatch.engineMatch([testEngine, baseEngine], games, timeControl, processes)

        # Print out match stats
        statString = results.statString()
        print(statString)
        outputString += statString + "\n"
        
    # Write output if needed
    if outputName:
        with open("output/" + outputName, "w") as file:
            file.write(outputString)