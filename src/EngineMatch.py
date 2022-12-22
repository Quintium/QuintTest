import time, signal, traceback
import chess, chess.engine
from multiprocessing import Pool, Manager
from tqdm import tqdm
from inspect import FrameInfo
from src.Results import Results, SharedResults, MatchEvent, ErrorEvent
from src.TimeControl import TimeControl, MatchTime

# Play match between two engines
def engineMatch(engines: list, games: int, timeControl: TimeControl, processes: int, totalGames: int) -> Results:
    # Handle keyboard interrupt in main process
    def handleKeyboardInterrupt(sig: int, frame: FrameInfo):
        sharedResults.stopMatch()

    # Create shared results
    manager = Manager()
    sharedResults = SharedResults(engines[0], engines[1], 0, 0, 0, timeControl, manager)

    # Create match output (engine names and progress bar)
    print(f"Engine match: {engines[0].fullName()} vs {engines[1].fullName()}")
    progressBar = tqdm(desc=f"Score: {sharedResults.scoreString()}", total=totalGames, dynamic_ncols=True, unit="games")

    # Create pool of processes
    with Pool(processes) as pool:
        # Distribute games across processes with same amount of white and black pieces
        inputs = [(i % 2, sharedResults) for i in range(games)]
        asyncResult = pool.starmap_async(engineGame, inputs)
        
        # Handle keyboard interrupts
        signal.signal(signal.SIGINT, handleKeyboardInterrupt)

        # Wait until games are ready
        while not asyncResult.ready():
            time.sleep(0.1)

            # Handle all events sent by child processes
            while sharedResults.hasEvent():
                event = sharedResults.getEvent()
                if isinstance(event, MatchEvent):
                    # Update score after completed match
                    progressBar.set_description(f"Score: {sharedResults.scoreString()}")
                    progressBar.update(1)
                elif isinstance(event, ErrorEvent):
                    # Output error after one is encountered
                    progressBar.write(event.error)

    # Cleanup
    progressBar.close()
    print()

    # Return pure results
    return sharedResults.toResults()

# Play an engine game in a child process
def engineGame(whiteEngine: int, results: SharedResults) -> None:
    # Ignore keyboard interrupts as they are handled by the main process
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    try:
        # Create processes from engines
        engineProcesses = [results.engine1.createProcess(), results.engine2.createProcess()]

        # Set up new match
        board = chess.Board()
        game = []
        matchTime = MatchTime(results.timeControl)
        gameResult = None
        
        # Play chess moves until the game ends or child process is aborted
        while (gameResult == None) and not results.wasStopped():
            # Check which engine's move it is
            moveTurn = board.turn
            engineNr = whiteEngine if moveTurn == chess.WHITE else not whiteEngine
            
            try:
                # Get the engine's move choice with the given time limit
                limit = matchTime.matchLimit()
                matchTime.start()
                moveResult = engineProcesses[engineNr].play(board, limit)
                matchTime.stop(moveTurn)
            except chess.engine.EngineError as e:
                # Handle engine errors by passing on a string of played moves to the error
                engineName = results.engine1.fullName() if engineNr == 0 else results.engine2.fullName()
                gameString = " ".join(game)
                raise chess.engine.EngineError(f"Engine error occured in engine '{engineName}' after moves: playing the moves '{gameString}'") from e
                
            # Play move on the board
            board.push(moveResult.move)
            game.append(moveResult.move.uci())

            gameResult = board.outcome(claim_draw=True)

            # Check if the engine flagged
            if matchTime.flagged():
                gameResult = chess.Outcome(chess.Termination(chess.Termination.VARIANT_LOSS), not moveTurn)

        # Close engines upon abortion
        if results.wasStopped():
            for engineProcess in engineProcesses:
                engineProcess.close()
            return

        # Check which color won
        winnerColor = gameResult.winner

        # Change results based on who won (or draw)
        if winnerColor == None:
            results.addDraws(1)
        else:
            if winnerColor == chess.WHITE:
                winnerEngine = whiteEngine
            else:
                winnerEngine = not whiteEngine

            if winnerEngine == 0:
                results.addEngine1Wins(1)
            else:
                results.addEngine2Wins(1)

        # Pass on that the event was completed
        results.putEvent(MatchEvent())

    # Send all errors to main process
    except Exception:
        results.putEvent(ErrorEvent(traceback.format_exc()))

    # Close engines (important)
    for engineProcess in engineProcesses:
        engineProcess.close()