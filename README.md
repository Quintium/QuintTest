# QuintTest
QuintTest is a CLI program for testing chess engines.

## Docs
### Installation
To install QuintTest, clone the repository and install the requirements with pip. Make sure pip is installed on your machine. Feel free to use venv to contain the installed libraries inside the project.

```
git clone https://github.com/Quintium/QuintTest
cd QuintTest
pip install -r requirements.txt
```

Afterwards, add the QuintTest directory to your PATH environment variable, so it can be accessed from any directory.

### Usage
To test engines, you can either put them into the `engines/` directory and run QuintTest from the QuintTest repository, or run QuintTest in a directory where all of the required engines are located. 

To run QuintTest, open the terminal in the desired directory and run your desired command:

```python src/QuintTest.py ...```

The available commands are:
- test

### `test`
The `test` command allows you to compare the performance of one or multiple chess engines against a base engine. It plays a specified number of games between the engines, using the specified time control per move. You can also specify the number of games to run simultaneously (concurrency), and the output path for the test results.

#### Usage
```QuintTest test TEST_ENGINES [TEST_ENGINES ...] BASE_ENGINE [OPTIONS]```

#### Options
```
-h, --help                              Show help message and exit                       optional
-g, --games GAMES                       Number of games to play in an engine match       required
-t, --time SECONDS                      Time control in seconds per move                 required
-c, --concurrency CONCURRENCY           Number of games to run simultaneously            optional - default: 1
-o, --output OUTPUT_NAME                Output name for test results                     optional - default: None
```

#### Example
```QuintTest test new_engine1 new_engine2 old_engine -g 1000 -t 0.1 -c 8 -o new_engine_test.out```

This command runs two engine matches: new_engine1 vs old_engine and new_engine2 vs old_engine - with 1000 games per match, 0.1s per move, 8 games running simultaneously - and outputs the results at new_engine_test.out.
