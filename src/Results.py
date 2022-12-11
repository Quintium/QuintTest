import math
from multiprocessing import Manager, Value, Lock, Queue, Event
from Engine import Engine

class Results:
    player1: Engine
    player2: Engine
    player1Wins: int
    player2Wins: int
    draws: int
    timeLimit: float

    def __init__(self, player1: Engine, player2: Engine, player1Wins: int, player2Wins: int, draws: int, timeLimit: float):
        self.player1 = player1
        self.player2 = player2
        self.player1Wins = player1Wins
        self.player2Wins = player2Wins
        self.draws = draws
        self.timeLimit = timeLimit

    def getPlayer1Wins(self) -> int:
        return self.player1Wins

    def getPlayer2Wins(self) -> int:
        return self.player2Wins

    def getDraws(self) -> int:
        return self.draws

    def addPlayer1Wins(self, n) -> None:
        self.player1Wins += n

    def addPlayer2Wins(self, n) -> None:
        self.player2Wins += n

    def addDraws(self, n) -> None:
        self.draws += n

    def gameAmount(self) -> int:
        return self.getPlayer1Wins() + self.getPlayer2Wins() + self.getDraws()

    def player1Score(self) -> int:
        return self.getPlayer1Wins() + self.getDraws() / 2

    def player2Score(self) -> int:
        return self.getPlayer2Wins() + self.getDraws() / 2

    def eloDifference(self) -> float:
        if self.gameAmount() == 0:
            return float("nan")

        expectedScore = self.player2Score() / self.gameAmount()
        if expectedScore == 0:
            return 10000
        elif expectedScore == 1:
            return -10000
        else:
            return round(400 * math.log10(1 / expectedScore - 1), 2)

    def eloDifferenceString(self) -> str:   
        eloDiff = self.eloDifference()
        return ("+" if eloDiff > 0 else "") + str(eloDiff)

    def los(self) -> float: # Likelihood of superiority
        if self.getPlayer1Wins() + self.getPlayer2Wins() == 0:
            return float("nan")
        if self.player1Wins == self.player2Wins:
            return 50
        unroundedLos = 0.5 * (1 + math.erf((self.getPlayer1Wins() - self.getPlayer2Wins()) / math.sqrt(2 * (self.getPlayer1Wins() + self.getPlayer2Wins()))))
        return round(unroundedLos * 100, 2)

    def scoreString(self):
        return f"{self.getPlayer1Wins()} - {self.getPlayer2Wins()} - {self.getDraws()}"

    def statString(self):
        message = (f"Engine match: {self.player1.fullName()} vs {self.player2.fullName()}:\n"
                   f"Time Limit: {self.timeLimit}\n"
                   f"Games played: {self.gameAmount()}\n"
                   f"Final score: {self.scoreString()}\n"
                   f"Elo difference: {self.eloDifferenceString()}\n"
                   f"Likelihood of superiority: {self.los()}%\n")

        return message

class SharedResults(Results):
    player1: Engine
    player2: Engine
    player1Wins: Value
    player2Wins: Value
    draws: Value
    timeLimit: float
    stop: Event
    lock: Lock
    eventQueue: Queue

    def __init__(self, player1: Engine, player2: Engine, player1Wins: int, player2Wins: int, draws: int, timeLimit: float, manager: Manager):
        self.player1 = player1
        self.player2 = player2
        self.player1Wins = manager.Value("i", player1Wins)
        self.player2Wins = manager.Value("i", player2Wins)
        self.draws = manager.Value("i", draws)
        self.timeLimit = timeLimit
        self.stop = manager.Event()
        self.lock = manager.Lock()
        self.eventQueue = manager.Queue()

    def getPlayer1Wins(self) -> int:
        return self.player1Wins.value

    def getPlayer2Wins(self) -> int:
        return self.player2Wins.value

    def getDraws(self) -> int:
        return self.draws.value

    def addPlayer1Wins(self, n) -> None:
        self.player1Wins.value += n

    def addPlayer2Wins(self, n) -> None:
        self.player2Wins.value += n

    def addDraws(self, n) -> None:
        self.draws.value += n

    def stopMatch(self) -> None:
        self.stop.set()

    def wasStopped(self) -> bool:
        return self.stop.is_set()

    def putEvent(self, event: Event) -> None:
        self.eventQueue.put(event)

    def hasEvent(self) -> bool:
        return not self.eventQueue.empty()

    def getEvent(self) -> Event:
        return self.eventQueue.get()

    def toResults(self) -> Results:
        return Results(self.player1, self.player2, self.getPlayer1Wins(), self.getPlayer2Wins(), self.getDraws(), self.timeLimit)

class Event:
    pass

class MatchEvent(Event):
    pass

class ErrorEvent(Event):
    error: str

    def __init__(self, error: str):
        self.error = error