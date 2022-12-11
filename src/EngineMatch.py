import time, signal, traceback
import chess, chess.engine
import multiprocessing, multiprocessing.pool
from multiprocessing import Pool, Manager, Value
from Results import Results, SharedResults, MatchEvent, ErrorEvent
from inspect import FrameInfo
from tqdm import tqdm

def playGames(gamesToPlay: int, results: SharedResults) -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    try:
        engineProcesses = [results.player1.createProcess(), results.player2.createProcess()]
        board = chess.Board()

        for i in range(gamesToPlay):
            board.reset()
            game = []
            whitePlayer = i % 2
            
            while (board.outcome(claim_draw=True) == None) and not results.wasStopped():
                engineNr = whitePlayer if board.turn == chess.WHITE else not whitePlayer
                result = engineProcesses[engineNr].play(board, chess.engine.Limit(time=results.timeLimit))
                    
                board.push(result.move)
                game.append(result.move.uci())

            if results.wasStopped():
                break

            winnerColor = board.outcome(claim_draw=True).winner

            with results.lock:
                if winnerColor == None:
                    results.addDraws(1)
                else:
                    if winnerColor == chess.WHITE:
                        winnerPlayer = whitePlayer
                    else:
                        winnerPlayer = not whitePlayer

                    if winnerPlayer == 0:
                        results.addPlayer1Wins(1)
                    else:
                        results.addPlayer2Wins(1)

            results.putEvent(MatchEvent())

    except Exception:
        results.putEvent(ErrorEvent(traceback.format_exc()))

    for engineProcess in engineProcesses:
        engineProcess.close()

def calculateTaskSize(games: int, processes: int) -> int:
    for n in range(1, games):
        taskSize = games / n
        if games % n == 0 and taskSize % 2 == 0 and taskSize * processes <= games: # task size has to be divisor, even and program should take more than one cycle
            return round(taskSize)

    raise RuntimeError("No fitting task size found, decrease number of processes or change to a more divisible number of games.")

def pairEngines(engines: list, games: int, timeLimit: float, processes: int, totalGames: int) -> Results:
    def handleKeyboardInterrupt(sig: int, frame: FrameInfo):
        sharedResults.stopMatch()

    if not processes:
        processes = int(multiprocessing.cpu_count() / 2)
    taskSize = calculateTaskSize(games, processes)

    manager = Manager()
    sharedResults = SharedResults(engines[0], engines[1], 0, 0, 0, timeLimit, manager)
    progressBar = tqdm(desc=f"Score: {sharedResults.scoreString()}", total=totalGames, dynamic_ncols=True, unit="games")

    with Pool(processes) as pool:
        inputs = [(taskSize, sharedResults)] * round(games / taskSize)
        asyncResult = pool.starmap_async(playGames, inputs)
        
        signal.signal(signal.SIGINT, handleKeyboardInterrupt)
        while not asyncResult.ready():
            time.sleep(0.01)
            while sharedResults.hasEvent():
                event = sharedResults.getEvent()
                if isinstance(event, MatchEvent):
                    progressBar.set_description(f"Score: {sharedResults.scoreString()}")
                    progressBar.update(1)
                elif isinstance(event, ErrorEvent):
                    progressBar.write(event.error)

    asyncResult.wait() 
    progressBar.close()
    print()

    return sharedResults.toResults()