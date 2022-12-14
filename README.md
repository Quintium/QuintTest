# QuintTest
QuintTest is a CLI program for testing chess engines.

## Docs
### Installation
#### Release
To install a released version of QuintTest, download the latest QuintTest release from GitHub. Extract the files and add the directory that QuintTest.exe is in to your PATH environment variable, so it can be accessed from any directory.

#### From source
To install QuintTest from the source, clone the repository and install the requirements with pip. Make sure git, Python and pip are installed on your machine. Feel free to use venv to contain the installed libraries inside the project.

```
git clone https://github.com/Quintium/QuintTest
cd QuintTest
pip install -r requirements.txt
```

Finally, add the QuintTest directory to your PATH environment variable, so it can be accessed from any directory. Make sure to regularly run `git pull` to stay up-to-date.

### Usage
To add an engine, you can either put it into the `engines/` directory or run QuintTest in a directory where the tested engine is located. 

To run a released version of QuintTest, run the following command in a terminal:

`QuintTest ...`

To run QuintTest from the source, run the following command in a terminal:

`python QuintTest.py ...`

The available commands are:
- test

### `test`
The `test` command allows you to compare the performance of one or multiple chess engines against a base engine. It plays a specified number of games between the engines, using the specified time control. You can also specify the number of games to run simultaneously (concurrency), and the output path for the test results.

#### Usage
```QuintTest test TEST_ENGINES [TEST_ENGINES ...] BASE_ENGINE [OPTIONS]```

#### Options
```
-h, --help                          Show help message and exit                          optional
-g, --games GAMES                   Number of games to play in an engine match          required
-t, --time TIMECONTROL              Time control, for example 5+0.1 for 5s base         required
                                    time and 0.1s increment and =0.2 for 0.2s 
                                    per move      
-c, --concurrency CONCURRENCY       Number of games to run simultaneously               optional - default: 1
-o, --output OUTPUT_NAME            Output name for test results                        optional - default: None
```

#### Example
```QuintTest test new_engine1 new_engine2 old_engine -g 1000 -t 0.1 -c 8 -o new_engine_test.out```

This command runs two engine matches: new_engine1 vs old_engine and new_engine2 vs old_engine - with 1000 games per match, 0.1s per move, 8 games running simultaneously - and outputs the results at new_engine_test.out.
