import sys, os, subprocess, errno
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

        # Save path of engine
        self.path = self.getPath()

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
            # Try to run file with path
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
        installedPath = os.path.dirname(os.path.abspath(sys.argv[0])) + "\\engines\\" + self.name
        if self.pathExec(installedPath):
            return installedPath
        
        # If no path is found return error
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), self.name)

    # Create engine process for engine
    def createProcess(self) -> chess.engine.SimpleEngine:
        return chess.engine.SimpleEngine.popen_uci([self.path] + [str(arg) for arg in self.args], setpgrp=True) # New process group, so keyboard interrupts aren't passed on