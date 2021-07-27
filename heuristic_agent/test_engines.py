import pstats

from heuristic_agent.engines.alphabeta import AlphaBetaEngine
from heuristic_agent.engines.alphabeta_cached import ABCachedEngine
from heuristic_agent.engines.alphabeta_cached_iterdeep import ABIterDeepEngine
from heuristic_agent.env.board import ChessBoard
import cProfile

def main():
    depth = 5
    alphabeta = AlphaBetaEngine(maxdepth=depth)
    alphabeta_cached = ABCachedEngine(maxdepth=depth)
    alphabeta_iterdeep = ABIterDeepEngine(maxdepth=depth)

    fen = "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/2PB1N2/PP1P1PPP/RNBQK2R w kq - 0 6"
    board = ChessBoard(fen)
    fen_black = "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/2PB1N2/PP1P1PPP/RNBQK2R b kq - 0 6"
    board_black = ChessBoard(fen_black)

    # best_moves_white = alphabeta.choose(board)
    # best_moves_black = alphabeta.choose(board_black)
    best_moves_white_cached = alphabeta_cached.choose(board)
    best_moves_black_cached = alphabeta_cached.choose(board_black)
    best_moves = alphabeta_iterdeep.choose(board)
    best_moves_black = alphabeta_iterdeep.choose(board_black)

    print("WHITE TO MOVE")
    for m in best_moves:
        print(m)

    print("\n\nBLACK TO MOVE")
    for m in best_moves_black:
        print(m)


if __name__=="__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('tottime')
    stats.print_stats()

