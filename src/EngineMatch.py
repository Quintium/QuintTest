import chess, chess.engine
import multiprocessing, multiprocessing.pool
from multiprocessing import Pool, Manager, Value
from Results import Results, SharedResults

def playGames(gamesToPlay: int, results: SharedResults) -> None:
    try:
        engineProcesses = [results.player1.createProcess(), results.player2.createProcess()]
        board = chess.Board()

        for i in range(gamesToPlay):
            board.reset()
            game = []
            whitePlayer = i % 2
            
            while (board.outcome(claim_draw=True) == None):
                engineNr = whitePlayer if board.turn == chess.WHITE else not whitePlayer
                try:
                    result = engineProcesses[engineNr].play(board, chess.engine.Limit(time=results.timeLimit))
                except chess.engine.EngineError as error:
                    gameString = " ".join(game)
                    engineName = results.player1.fullName() if engineNr == 0 else results.player2.fullName()
                    print(f"Error '{error}' occured in engine {engineName} after playing the moves: '{gameString}'")
                    print(f"Aborting process...")

                    results.stopMatch()
                    for engineProcess in engineProcesses:
                        engineProcess.close()
                    return results
                    
                board.push(result.move)
                game.append(result.move.uci())

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

                results.printScore()

            if results.wasStopped():
                print("Aborting process...\n")
                break
    except Exception as err:
        print(Exception, err)
        print("Aborting process...\n")
        results.stopMatch()

    for engineProcess in engineProcesses:
        engineProcess.close()

def calculateTaskSize(games: int, processes: int) -> int:
    for n in range(1, games):
        taskSize = games / n
        if games % n == 0 and taskSize % 2 == 0 and taskSize * processes <= games: # task size has to be divisor, even and program should take more than one cycle
            return round(taskSize)

    raise RuntimeError("No fitting task size found, decrease number of processes or change to a more divisible number of games.")

def pairEngines(engines: list, games: int, timeLimit: float, processes: int, totalGames: int) -> Results:
    global pool
    if not processes:
        processes = int(multiprocessing.cpu_count() / 2)
    taskSize = calculateTaskSize(games, processes)

    manager = Manager()
    sharedResults = SharedResults(engines[0], engines[1], 0, 0, 0, timeLimit, totalGames, manager)
    sharedResults.printScore()

    with Pool(processes) as pool:
        inputs = [(taskSize, sharedResults)] * round(games / taskSize)
        try:
            pool.starmap(playGames, inputs)
        except Exception as err:
            print(Exception, err)
            sharedResults.stopMatch()

    print()
    print()

    return sharedResults.toResults()