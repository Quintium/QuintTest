import time
import chess, chess.engine

# Class for holding time control information
class TimeControl:
    baseTime: float
    increment: float
    exactTime: float

    # Extract time control information from string: ("3+0.1" -> baseTime 3, increment: 0.1; "=5": exactTime 5)
    def __init__(self, tcString: str):
        if tcString[0] == "=":
            # Extract exact time per move
            self.exactTime = float(tcString[1:])
            self.baseTime = None
            self.increment = None
        else:
            self.exactTime = None
            if "+" in tcString:
                # Extract time with increment
                self.baseTime = float(tcString[:tcString.index("+")])
                self.increment = float(tcString[tcString.index("+") + 1:])
            else:
                # Extract time without increment
                self.baseTime = float(tcString)
                self.increment = 0

    # Convert time control back to string
    def toString(self) -> str:
        if self.exactTime == None:
            return str(self.baseTime) + "+" + str(self.increment)
        else:
            return "=" + str(self.exactTime)

# Class for managing time in a match
class MatchTime:
    timeControl: TimeControl
    whiteTime: float
    blackTime: float
    startTime: float
    
    # Set up start of match
    def __init__(self, timeControl: TimeControl) -> None:
        self.timeControl = timeControl
        self.whiteTime = timeControl.baseTime
        self.blackTime = timeControl.baseTime

    # Return search stop condition
    def matchLimit(self) -> chess.engine.Limit:
        if self.timeControl.exactTime == None:
            # Handle sudden death time limit
            return chess.engine.Limit(white_clock=self.whiteTime, black_clock=self.blackTime, white_inc=self.timeControl.increment, black_inc=self.timeControl.increment)
        else:
            # Handle fixed time limit
            return chess.engine.Limit(time=self.timeControl.exactTime)

    # Start clock
    def start(self) -> None:
        self.startTime = time.time()

    # Stop clock, deduct used time
    def stop(self, turn: chess.Color) -> None:
        timePassed = time.time() - self.startTime
        self.startTime = None

        # Deduct time used
        if self.timeControl.exactTime == None:
            if turn == chess.WHITE:
                self.whiteTime -= timePassed
            else:
                self.blackTime -= timePassed

    # Check if engine that moved flagged
    def flagged(self):
        if self.timeControl.exactTime == None:
            return self.whiteTime <= 0 or self.blackTime <= 0
        else:
            return False
        

