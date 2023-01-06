import sys, yaml
from yaml.loader import SafeLoader
import src.EngineMatch
from src.Engine import Engine
from src.TimeControl import TimeControl

def main():
    # Check if there are sufficient arguments
    if len(sys.argv) < 5:
        sys.stderr.write("Too few arguments\n")
        return 2

    # Parse seed
    try:
        seed = int(sys.argv[2])
    except:
        sys.stderr.write(f"Invalid seed value: {sys.argv[2]}\n")
        return 2

    # Parse engine parameters
    try:
        engineParams = [float(param) for param in sys.argv[4::2]]
    except:
        sys.stderr.write(f"Invalid parameter values\n")
        return 2

    # Parse options for testing from yaml file
    try:
        with open("clop-quinttest-options.yaml", "r") as file:
            data = yaml.load(file, Loader=SafeLoader)
            engineName = data["engine_name"]
            opponentName = data["opponent_name"]
            opponentParams = data["opponent_parameters"]
            timeControlString = data["time_control"]
    except:
        sys.stderr.write(f"Insufficient/invalid options in clop-quinttest-options.yaml\n")
        return 2

    # Create engine objects, determine who's white from the seed
    engine1 = Engine(engineName, engineParams)
    engine2 = Engine(opponentName, opponentParams)
    if seed % 2 == 1:
        engine1, engine2 = engine2, engine1

    # Create time control object
    timeControl = TimeControl(timeControlString)

    # Complete engine match
    try:
        results = src.EngineMatch.engineMatch([engine1, engine2], 1, timeControl, 1, True)
    except:
        sys.stderr.write("Engine match failed\n")
        return 1

    # Check which engine won
    if results.getEngine1Wins() == 1:
        result = 1
    elif results.getEngine2Wins() == 1:
        result = 0
    else:
        result = 0.5

    # Adjust results for white/black
    if seed % 2 == 1:
        result = 1 - result

    # Print out results
    if result == 1:
        sys.stdout.write('W\n')
    elif result == 0:
        sys.stdout.write('L\n')
    else:
        sys.stdout.write('D\n')

    return 0

if __name__ == "__main__":
    sys.exit(main())