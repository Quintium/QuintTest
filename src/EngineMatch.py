import time, signal, traceback
import multiprocessing
import chess, chess.engine
from multiprocessing import Pool, Manager
from tqdm import tqdm
from inspect import FrameInfo
from Results import Results, SharedResults, MatchEvent, ErrorEvent

def pairEngines(engines: list, games: int, timeLimit: float, processes: int, totalGames: int) -> Results:
    def handleKeyboardInterrupt(sig: int, frame: FrameInfo):
        sharedResults.stopMatch()

    if games % 2 == 1:
        raise RuntimeError("Game amount has to be even, so the amount of white and black games is the same.")

    manager = Manager()
    sharedResults = SharedResults(engines[0], engines[1], 0, 0, 0, timeLimit, manager)
    progressBar = tqdm(desc=f"Score: {sharedResults.scoreString()}", total=totalGames, dynamic_ncols=True, unit="games")

    with Pool(processes) as pool:
        inputs = [(2, sharedResults)] * round(games / 2)
        asyncResult = pool.starmap_async(playGames, inputs)
        
        signal.signal(signal.SIGINT, handleKeyboardInterrupt)
        while not asyncResult.ready():
            time.sleep(0.1)
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
                
                try:
                    result = engineProcesses[engineNr].play(board, chess.engine.Limit(time=results.timeLimit))
                except chess.engine.EngineError as e:
                    engineName = results.player1.fullName() if engineNr == 0 else results.player2.fullName()
                    gameString = " ".join(game)
                    raise chess.engine.EngineError(f"Engine error occured in engine '{engineName}' after moves: playing the moves '{gameString}'") from e
                    
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