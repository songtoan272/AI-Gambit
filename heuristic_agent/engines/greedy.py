import chess

from heuristic_agent.env.board import ChessBoard
from heuristic_agent.engines.base import Engine
from heuristic_agent.env.eval import INF, evaluate


class GreedyEngine(Engine):
    """
    Implementation of simple Greedy Minimax with a shallow depth of 1
    As the implementation of the evaluate function takes into account the player turn therefore
    the greedy Minimax engine can be implemented in a negamax way
    """
    def __init__(self):
        self.evaluate = evaluate

    def choose(self, board: ChessBoard):
        bestmove = chess.Move.null()
        bestscore = -INF

        for m in board.moves:
            board.push(m)
            score = -self.evaluate(board)
            board.pop()
            if score > bestscore:
                bestmove = m
                bestscore = score

        print('Best score: ', bestscore)
        print('Best move: ', bestmove)

        return bestmove, bestscore



    def __str__(self):
        return "Greedy"
