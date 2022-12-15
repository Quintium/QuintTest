import os, shutil
import chess, chess.engine

# Class for managing engines and their executables
class Engine:
    name: str
    args: list

    # Create engine based on name and command line arguments
    def __init__(self, name, args):
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

    # Get path of engine executable
    def path(self) -> None:
        # Check if file exists in main directory
        if shutil.which(self.name, os.X_OK):
            return self.name

        # Check if file exists in engine directory
        if shutil.which("engines/" + self.name, os.X_OK):
            return "engines/" + self.name
        
        raise RuntimeError(f"No executable found at [engines\]{self.name}")

    # Create engine process for engine
    def createProcess(self) -> chess.engine.SimpleEngine:
        return chess.engine.SimpleEngine.popen_uci([self.path()] + [str(arg) for arg in self.args], setpgrp=True) # New process group, so keyboard interrupts aren't passed on