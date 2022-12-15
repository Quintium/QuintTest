import argparse
import multiprocessing
import Test

if __name__ == "__main__":
    multiprocessing.freeze_support()

    arger = argparse.ArgumentParser()

    subparsers = arger.add_subparsers(dest="command")
    
    testParser = subparsers.add_parser("test")
    testParser.add_argument("testEngines", nargs="+", type=str)
    testParser.add_argument("baseEngine", type=str)
    testParser.add_argument("-g", "--games", type=int, required=True, dest="games", help="number of games that are played")
    testParser.add_argument("-t", "--time", type=float, required=True, dest="timeLimit", help="time control per move")
    testParser.add_argument("-c", "--concurrency", default=1, type=int,  dest="concurrency", help="number of games simultaneously")
    testParser.add_argument("-o", "--output", default=None, type=str,  dest="outputPath", help="output path of the test results")
    options = arger.parse_args()

    if options.command == "test":
        Test.test(options.testEngines, options.baseEngine, options.games, options.timeLimit, options.concurrency, options.outputPath)