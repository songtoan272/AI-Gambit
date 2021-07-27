from typing import Tuple, List

import chess

from heuristic_agent.env.board import ChessBoard
from heuristic_agent.env.eval import INF
from heuristic_agent.engines.greedy import GreedyEngine


class NegamaxEngine(GreedyEngine):
    FORMAT_STAT = (
            'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, maxdepth=2):
        super().__init__()
        self._maxdepth = int(maxdepth)

    def choose(self, board) -> chess.Move:
        self.initcounter()
        pv, score = self.search(board, self._maxdepth)

        self.showstats(pv, score)

        return pv[0]

    def search(self, board: ChessBoard, depth: int, ply=0) -> Tuple[List[chess.Move], int]:
        """
        Search best move from the current board state using negamax implementation
        :param board: representation of board
        :param depth: depth left to search
        :param ply: number of depth (half-move) already searched
        :return: sequence of moves to go from the current board to the best found and the corresponding score
        """
        self.inc('nodes')

        if board.end is not None:
            self.inc('leaves')
            if board.end == 0:
                self.inc('draws')
            else:
                self.inc('mates')
            return [], -self.evaluate(board)

        if depth <= 0:
            self.inc('leaves')
            return [], -self.evaluate(board)

        bestmove = []
        bestscore = -INF
        for m in board.moves:
            board.push(m)
            nextmoves, score = self.search(board, depth - 1, ply + 1)
            board.pop()
            if not bestmove or score >= bestscore:
                bestscore = score
                bestmove = [m] + nextmoves

        return bestmove, -bestscore

    def endscore(self, board, ply):
        self.inc('leaves')
        if board.end == 0:
            self.inc('draws')
        else:
            self.inc('mates')
        return [], -(self.evaluate(board) - ply * (1 if board.turn else -1))

    def __str__(self):
        return 'Negamax(%s)' % self._maxdepth
