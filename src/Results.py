import math
from multiprocessing import Manager, Value, Lock, Queue, Event
from Engine import Engine

# Class that contains results of an engine match
class Results:
    engine1: Engine
    engine2: Engine
    engine1Wins: int
    engine2Wins: int
    draws: int
    timeLimit: float

    # Create results based ong given stats
    def __init__(self, engine1: Engine, engine2: Engine, engine1Wins: int, engine2Wins: int, draws: int, timeLimit: float):
        self.engine1 = engine1
        self.engine2 = engine2
        self.engine1Wins = engine1Wins
        self.engine2Wins = engine2Wins
        self.draws = draws
        self.timeLimit = timeLimit

    # Get match stats
    def getEngine1Wins(self) -> int:
        return self.engine1Wins

    def getEngine2Wins(self) -> int:
        return self.engine2Wins

    def getDraws(self) -> int:
        return self.draws

    # Change match stats
    def addEngine1Wins(self, n) -> None:
        self.engine1Wins += n

    def addEngine2Wins(self, n) -> None:
        self.engine2Wins += n

    def addDraws(self, n) -> None:
        self.draws += n

    # More match stats not stored in variables
    def gameAmount(self) -> int:
        return self.getEngine1Wins() + self.getEngine2Wins() + self.getDraws()

    def engine1Score(self) -> int:
        return self.getEngine1Wins() + self.getDraws() / 2

    def engine2Score(self) -> int:
        return self.getEngine2Wins() + self.getDraws() / 2

    # Calculate elo difference of engines after match
    def eloDifference(self) -> float:
        if self.gameAmount() == 0:
            return float("nan")

        expectedScore = self.engine2Score() / self.gameAmount()
        if expectedScore == 0:
            return 10000
        elif expectedScore == 1:
            return -10000
        else:
            return round(400 * math.log10(1 / expectedScore - 1), 2)

    # Convert elo difference to string
    def eloDifferenceString(self) -> str:   
        eloDiff = self.eloDifference()
        return ("+" if eloDiff > 0 else "") + str(eloDiff)

    # Calculate likelihood of superiority: likelihood that engine 1 is superior to engine 2
    def los(self) -> float:
        if self.getEngine1Wins() + self.getEngine2Wins() == 0:
            return float("nan") # No LOS calculatable
        unroundedLos = 0.5 * (1 + math.erf((self.getEngine1Wins() - self.getEngine2Wins()) / math.sqrt(2 * (self.getEngine1Wins() + self.getEngine2Wins()))))
        return round(unroundedLos * 100, 2)

    # Create string out of score
    def scoreString(self):
        return f"{self.getEngine1Wins()} - {self.getEngine2Wins()} - {self.getDraws()}"

    # Convert stats to multi-line string
    def statString(self):
        message = (f"Engine match: {self.engine1.fullName()} vs {self.engine2.fullName()}:\n"
                   f"Time Limit: {self.timeLimit}\n"
                   f"Games played: {self.gameAmount()}\n"
                   f"Final score: {self.scoreString()}\n"
                   f"Elo difference: {self.eloDifferenceString()}\n"
                   f"Likelihood of superiority: {self.los()}%\n")

        return message

# Class for sharing results between processes using multiprocessing
class SharedResults(Results):
    engine1: Engine
    engine2: Engine
    engine1Wins: Value
    engine2Wins: Value
    draws: Value
    timeLimit: float
    stop: Event # Event for stopping match prematurely
    lock: Lock # Lock for incrementing wins/draws
    eventQueue: Queue # Queue for events from child processes to main process

    # Create shared results using stats and multiprocessing manager
    def __init__(self, engine1: Engine, engine2: Engine, engine1Wins: int, engine2Wins: int, draws: int, timeLimit: float, manager: Manager):
        self.engine1 = engine1
        self.engine2 = engine2
        self.engine1Wins = manager.Value("i", engine1Wins)
        self.engine2Wins = manager.Value("i", engine2Wins)
        self.draws = manager.Value("i", draws)
        self.timeLimit = timeLimit
        self.stop = manager.Event()
        self.lock = manager.Lock()
        self.eventQueue = manager.Queue()

    # Get match stats
    def getEngine1Wins(self) -> int:
        return self.engine1Wins.value

    def getEngine2Wins(self) -> int:
        return self.engine2Wins.value

    def getDraws(self) -> int:
        return self.draws.value

    # Change match stats (with lock since increments of multiprocessing.Value are not atomic)
    def addEngine1Wins(self, n) -> None:
        with self.lock:
            self.engine1Wins.value += n

    def addEngine2Wins(self, n) -> None:
        with self.lock:
            self.engine2Wins.value += n

    def addDraws(self, n) -> None:
        with self.lock:
            self.draws.value += n

    # Stopping matches
    def stopMatch(self) -> None:
        self.stop.set()

    def wasStopped(self) -> bool:
        return self.stop.is_set()

    # Managing events
    def putEvent(self, event: Event) -> None:
        self.eventQueue.put(event)

    def hasEvent(self) -> bool:
        return not self.eventQueue.empty()

    def getEvent(self) -> Event:
        return self.eventQueue.get()

    # Converting to pure results object
    def toResults(self) -> Results:
        return Results(self.engine1, self.engine2, self.getEngine1Wins(), self.getEngine2Wins(), self.getDraws(), self.timeLimit)

# General class for events
class Event:
    pass

# Event for completed match
class MatchEvent(Event):
    pass

# Event for error encountered
class ErrorEvent(Event):
    error: str

    def __init__(self, error: str):
        self.error = error