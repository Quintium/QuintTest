import math
from multiprocessing import Manager, Value, Lock
from Engine import Engine

class Results:
    player1: Engine
    player2: Engine
    player1Wins: int
    player2Wins: int
    draws: int
    timeLimit: float

    def __init__(self, player1: Engine, player2: Engine, player1Wins: int, player2Wins: int, draws: int, timeLimit: float, gameTarget: int):
        self.player1 = player1
        self.player2 = player2
        self.player1Wins = player1Wins
        self.player2Wins = player2Wins
        self.draws = draws
        self.timeLimit = timeLimit
        self.gameTarget = gameTarget

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

    def printScore(self):
        progressLength = 40

        progress = self.gameAmount() / self.gameTarget
        percentage = format(progress * 100, ".2f")
        progressChars = round(progress * progressLength)
        progressBar = f"[{'=' * progressChars}{'>' if progressChars < progressLength else ''}{'.' * (progressLength - progressChars - 1)}]"
        print(f"Match: {self.player1.fullName()} - {self.player2.fullName()}; Progress: {progressBar} {percentage}%; Score: {self.getPlayer1Wins()} - {self.getPlayer2Wins()} - {self.getDraws()}", end="\r")

    def statString(self):
        message = ""
        message += f"Engine match: {self.player1.fullName()} vs {self.player2.fullName()}:\n"
        message += f"Time Limit: {self.timeLimit}\n"
        message += f"Games played: {self.gameAmount()}\n"
        message += f"Final score: {self.getPlayer1Wins()} - {self.getPlayer2Wins()} - {self.getDraws()}\n"
        message += f"Elo difference: {self.eloDifferenceString()}\n"
        message += f"Likelihood of superiority: {self.los()}%\n"
        message += "\n"

        return message

class SharedResults(Results):
    player1: Engine
    player2: Engine
    player1Wins: Value
    player2Wins: Value
    draws: Value
    timeLimit: float
    stop: Value
    lock: Lock

    def __init__(self, player1: Engine, player2: Engine, player1Wins: int, player2Wins: int, draws: int, timeLimit: float, gameTarget: int, manager: Manager):
        self.player1 = player1
        self.player2 = player2
        self.player1Wins = manager.Value("i", player1Wins)
        self.player2Wins = manager.Value("i", player2Wins)
        self.draws = manager.Value("i", draws)
        self.timeLimit = timeLimit
        self.gameTarget = gameTarget
        self.stop = manager.Value("i", 0)
        self.lock = manager.Lock()

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

    def wasStopped(self) -> bool:
        return self.stop.value == 1

    def stopMatch(self) -> None:
        self.stop.value = 1

    def toResults(self) -> Results:
        return Results(self.player1, self.player2, self.getPlayer1Wins(), self.getPlayer2Wins(), self.getDraws(), self.timeLimit, self.gameTarget)