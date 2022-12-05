import chess, chess.engine
import multiprocessing, multiprocessing.pool
from multiprocessing import Pool, Manager, Value
from Results import Results, SharedResults

def playGames(gamesToPlay: int, engines: list, timeLimit: float, player1Wins: Value, player2Wins: Value, draws: Value, stop: Value) -> None:
    try:
        results = SharedResults(engines[0], engines[1], player1Wins, player2Wins, draws, timeLimit)
        engineProcesses = [engine.createProcess() for engine in engines]
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

                    stop.value = 1
                    for engineProcess in engineProcesses:
                        engineProcess.close()
                    return results
                    
                board.push(result.move)
                game.append(result.move.uci())

            winnerColor = board.outcome(claim_draw=True).winner

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

            print(f"Game played: {results.player1.fullName()} vs {results.player2.fullName()}")
            print(f"Score: {results.getPlayer1Wins()} - {results.getPlayer2Wins()} - {results.getDraws()}")

            if stop.value == 1:
                print("Aborting process...")
                break
    except Exception as err:
        print(Exception, err)
        print("Aborting process...")
        stop.value = 1

    for engineProcess in engineProcesses:
        engineProcess.close()

def calculateTaskSize(games: int, processes: int) -> int:
    for n in range(1, games):
        taskSize = games / n
        if games % n == 0 and taskSize % 2 == 0 and taskSize * processes <= games: # task size has to be divisor, even and program should take more than one cycle
            return round(taskSize)

    raise RuntimeError("No fitting task size found, decrease number of processes or change to a more divisible number of games.")

def pairEngines(engines: list, games: int, timeLimit: float, processes: int) -> Results:
    global pool
    if not processes:
        processes = int(multiprocessing.cpu_count() / 2)
    taskSize = calculateTaskSize(games, processes)

    manager = Manager()

    wins1 = manager.Value("i", 0)
    wins2 = manager.Value("i", 0)
    draws = manager.Value("i", 0)
    stop = manager.Value("i", 0)

    with Pool(processes) as pool:
        inputs = [(taskSize, engines, timeLimit, wins1, wins2, draws, stop)] * round(games / taskSize)
        try:
            pool.starmap(playGames, inputs)
        except Exception as err:
            print(Exception, err)
            stop.value = 1

    results = Results(engines[0], engines[1], wins1.value, wins2.value, draws.value, timeLimit)
    return results