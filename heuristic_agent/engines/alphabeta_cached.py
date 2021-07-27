from typing import Tuple, List
import chess

from heuristic_agent.enhancements.killer_moves import KillerMoves
from heuristic_agent.env.board import ChessBoard
from heuristic_agent.engines.alphabeta import AlphaBetaEngine
from heuristic_agent.env.eval import INF
from heuristic_agent.enhancements.transposition_table import TranspositionTable, Flag, Entry


class ABCachedEngine(AlphaBetaEngine):
    FORMAT_STAT = (
            'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
            'hits: {hits}, leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, maxdepth=2, ordering='cache', maxitems=1024000, nb_killers=2):
        super(ABCachedEngine, self).__init__(maxdepth, ordering)
        self._cache = TranspositionTable(maxitems)
        self._killers = KillerMoves(maxdepth, nb_killers)
        self.moveorder.set_tt(self._cache)
        self.moveorder.set_km(self._killers)

    def initcounter(self):
        super(ABCachedEngine, self).initcounter()
        self._counters['hits'] = 0

    def search(self, board: ChessBoard, depth, ply=0, alpha=-INF, beta=INF) -> Tuple[List[chess.Move], int]:
        orig_alpha = alpha
        ttEntry: Entry = self._cache.retrieve(board)
        if ttEntry and ttEntry.depth >= depth:
            self.inc('hits')
            if ttEntry.flag is Flag.EXACT:
                return [ttEntry.move], ttEntry.score
            elif ttEntry.flag is Flag.LOWERBOUND and ttEntry.score > alpha:
                alpha = ttEntry.score
            elif ttEntry.flag is Flag.UPPERBOUND and ttEntry.score < beta:
                beta = ttEntry.score

            if alpha >= beta:
                if not board.is_capture(ttEntry.move):
                    self._killers.insert_killer(ttEntry.move, ply)
                return [ttEntry.move], ttEntry.score

        self.inc('nodes')

        if board.end is not None:
            self.inc('leaves')
            if board.end == 0:
                self.inc('draws')
            else:
                self.inc('mates')
            board_score = self.evaluate(board)
            self._cache.put(board, chess.Move.null(), depth, ply, board_score, alpha, beta)
            return [], board_score

        elif depth == 0:
            self.inc('leaves')
            board_score = self.evaluate(board)
            self._cache.put(board, chess.Move.null(), depth, ply, board_score, alpha, beta)
            # return [], self.quiesce(board, alpha, beta)
            return [], board_score

        else:
            bestmove = []
            bestscore = -INF - 1
            # examine all other possible moves
            for m in self.order(board, ply):
                board.push(m)
                nextmoves, score = self.search(board, depth - 1, ply + 1, -beta, -alpha)
                board.pop()
                score = -score
                if not bestmove or score > bestscore:
                    bestscore = score
                    bestmove = [m] + nextmoves
                if bestscore > alpha:
                    alpha = bestscore

                if bestscore >= beta:
                    self.inc('betacuts')
                    if alpha >= beta:
                        if not board.is_capture(m):
                            self._killers.insert_killer(m, ply)
                    break
            self._cache.put(board, bestmove[0], depth, ply, bestscore, alpha, beta)
            return bestmove, bestscore

    def __str__(self):
        return 'AlphaBetaCache(%s)' % self._maxdepth
