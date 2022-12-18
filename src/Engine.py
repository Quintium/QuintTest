import os, shutil, glob, subprocess
import chess, chess.engine

# Class for managing engines and their executables
class Engine:
    name: str
    args: list

    # Create engine based on name and command line arguments
    def __init__(self, name: str, args: list):
        self.name = name
        self.args = args

    # Give full name of engine, potentially stripping of .exe and adding command line arguments
    def fullName(self) -> str:
        name = self.name

        # Omit file extension
        if "." in name:
            name = name[: name.find(".")]
        
        # Add command line arguments to name
        if self.args:
            name += "_".join([str(arg) for arg in self.args])

        return name

    # Check if a path points to an executable
    def pathExec(self, path: str) -> bool:
        try:
            # Try to run file with path, exit after 1ms, return False if file exits after less than 1ms (engines should wait for output)
            subprocess.run(path, check=True, timeout=0.001, stdout=subprocess.DEVNULL)
            return False
        except FileNotFoundError:
            # Return False if file isn't found
            return False
        except subprocess.CalledProcessError:
            # Return False if file can't be called
            return False
        except subprocess.TimeoutExpired:
            # Return True if file runs more than 1ms
            return True

    # Get path of engine executable
    def path(self) -> None:
        # Check if file exists in main directory
        if self.pathExec(self.name):
            return self.name

        # Check if file exists in engine directory
        if self.pathExec("engines/" + self.name):
            return "engines/" + self.name
        
        raise RuntimeError(f"No executable found at [engines\]{self.name}")

    # Create engine process for engine
    def createProcess(self) -> chess.engine.SimpleEngine:
        return chess.engine.SimpleEngine.popen_uci([self.path()] + [str(arg) for arg in self.args], setpgrp=True) # New process group, so keyboard interrupts aren't passed on