import os, shutil, glob, subprocess, errno
import chess, chess.engine

# Class for managing engines and their executables
class Engine:
    name: str
    args: list
    path: str

    # Create engine based on name and command line arguments
    def __init__(self, name: str, args: list):
        self.name = name
        self.args = args

        # Save path of engine, if no path is found return error
        self.path = self.getPath()
        if self.path == None:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), "[engines/]" + self.name)

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
            p = subprocess.Popen(path, stdout=subprocess.DEVNULL)
            p.terminate()
            return True
        except OSError:
            # Return False if file isn't found
            return False
        except subprocess.CalledProcessError:
            # Return False if file returns error
            return False

    # Get path of engine executable
    def getPath(self) -> None:
        # Check if file exists in main directory
        if self.pathExec(self.name):
            return self.name

        # Check if file exists in engine directory
        if self.pathExec("engines/" + self.name):
            return "engines/" + self.name
        
        return None

    # Create engine process for engine
    def createProcess(self) -> chess.engine.SimpleEngine:
        return chess.engine.SimpleEngine.popen_uci([self.path] + [str(arg) for arg in self.args], setpgrp=True) # New process group, so keyboard interrupts aren't passed on