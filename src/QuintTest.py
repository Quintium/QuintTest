import argparse
import multiprocessing
import Test

if __name__ == "__main__":
    # Is needed for some reason
    multiprocessing.freeze_support()

    # Create parser for command line arguments
    arger = argparse.ArgumentParser()
    subparsers = arger.add_subparsers(dest="command")
    
    # Create parser for test command
    testParser = subparsers.add_parser("test")
    testParser.add_argument("testEngines", nargs="+", type=str)
    testParser.add_argument("baseEngine", type=str)
    testParser.add_argument("-g", "--games", type=int, required=True, dest="games", help="number of games per match")
    testParser.add_argument("-t", "--time", type=float, required=True, dest="timeLimit", help="time control per move")
    testParser.add_argument("-c", "--concurrency", default=1, type=int,  dest="concurrency", help="number of games simultaneously")
    testParser.add_argument("-o", "--output", default=None, type=str,  dest="outputName", help="output name for test results")
    
    # Parse command line arguments
    options = arger.parse_args()

    # Execute command
    if options.command == "test":
        Test.test(options.testEngines, options.baseEngine, options.games, options.timeLimit, options.concurrency, options.outputName)