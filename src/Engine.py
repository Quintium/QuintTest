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
        return (self.name[:-4] if self.name.endswith(".exe") else self.name) + ("_" if self.args else "") + "_".join([str(arg) for arg in self.args])

    # Create engine process for engine
    def createProcess(self) -> chess.engine.SimpleEngine:
        return chess.engine.SimpleEngine.popen_uci(["engines/" + self.name] + [str(arg) for arg in self.args], setpgrp=True) # New process group, so keyboard interrupts aren't passed on