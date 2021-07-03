from typing import List, Tuple, Generator

import chess

from heuristic_agent.board import ChessBoard
from heuristic_agent.transposition_table import TranspositionTable, Flag, Entry
from heuristic_agent.evaluate import INF
from heuristic_agent.engines.negamax import NegamaxEngine
from heuristic_agent.moveordering import MoveOrdering


class AlphaBetaEngine(NegamaxEngine):
    FORMAT_STAT = (
            'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
            'leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, maxdepth=2, ordering='seq'):
        super().__init__(maxdepth)
        self.moveorder = MoveOrdering(ordering).order

    def initcounter(self):
        super(AlphaBetaEngine, self).initcounter()
        self._counters['betacuts'] = 0

    def search(self, board: ChessBoard, depth, ply=0, alpha=-INF, beta=INF):
        self.inc('nodes')

        if board.end is not None:
            self.inc('leaves')
            if board.end == 0:
                self.inc('draws')
            else:
                self.inc('mates')
            return [], self.evaluate(board)

        if depth <= 0:
            self.inc('leaves')
            # return [], self.quiesce(board, alpha, beta)
            return [], self.evaluate(board)

        bestmove = []
        bestscore = -INF - 1
        for m in self.moveorder(board):
            board.push(m)
            nextmoves, score = self.search(board, depth - 1, ply + 1, -beta, -alpha)
            board.pop()
            score = -score
            if not bestmove or score > bestscore:
                bestscore = score
                bestmove = [m] + nextmoves
            if score > alpha:
                alpha = score

            if alpha >= beta:
                self.inc('betacuts')
                break

        return bestmove, alpha

    def quiesce(self, board, alpha: int, beta: int) -> int:
        # https://www.chessprogramming.org/Quiescence_Search
        stand_pat = self.evaluate(board)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        for move in board.moves:
            if board.is_capture(move):
                board.push(move)
                score = -self.quiesce(board, -beta, -alpha)
                board.pop()
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha

    def __str__(self):
        return 'AlphaBeta(%s)' % self._maxdepth


class ABCachedEngine(AlphaBetaEngine):
    FORMAT_STAT = (
            'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
            'hits: {hits}, leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, maxdepth=2, ordering='eval', maxitems=500000):
        super(ABCachedEngine, self).__init__(maxdepth, ordering)
        self._cache = TranspositionTable(maxitems)

    def initcounter(self):
        super(ABCachedEngine, self).initcounter()
        self._counters['hits'] = 0

    # def _search(self, board, depth, ply=0, alpha=-INF, beta=INF) -> Tuple[List[chess.Move], int]:
    #     # Look up in the tranposition table if the board position was already searched
    #     hit, move, score = self._cache.lookup(board, depth, ply, alpha, beta)
    #     if hit:
    #         self.inc('hits')
    #         if move is not None:
    #             bestmove = [move]
    #         else:
    #             bestmove = []
    #         return bestmove, score
    #     else:
    #         bestmove, score = super(ABCachedEngine, self).search(board, depth, ply, alpha, beta)
    #         self._cache.put(board, bestmove, depth, ply, score, alpha, beta)
    #         return bestmove, score

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

            if alpha > beta:
                return [ttEntry.move], ttEntry.score

        self.inc('nodes')

        if board.end is not None:
            self.inc('leaves')
            if board.end == 0:
                self.inc('draws')
            else:
                self.inc('mates')
            board_score = self.evaluate(board)
            self._cache.put(board, [], depth, ply, board_score, orig_alpha, beta)
            return [], board_score

        elif depth == 0:
            self.inc('leaves')
            board_score = self.evaluate(board)
            self._cache.put(board, [], depth, ply, board_score, orig_alpha, beta)
            # return [], self.quiesce(board, alpha, beta)
            return [], board_score

        else:
            bestmove = []
            bestscore = -INF - 1
            # examine entry move first if exist
            if ttEntry and ttEntry.depth > 0:
                board.push(ttEntry.move)
                nextmoves, score = self.search(board, depth-1, ply+1, -beta, -alpha)
                board.pop()
                score = -score
                bestmove = [ttEntry.move]
                if not bestmove or score > bestscore:
                    bestscore = score
                    bestmove = [ttEntry.move] + nextmoves
                if score > alpha:
                    alpha = score
                if bestscore >= beta:
                    self.inc('betacuts')
                self._cache.put(board, bestmove, depth, ply, bestscore, orig_alpha, beta)
                return bestmove, bestscore
            # examine all other possible moves
            for m in self.moveorder(board, self._cache):
                if ttEntry and ttEntry.move == m:
                    continue
                board.push(m)
                nextmoves, score = self.search(board, depth - 1, ply + 1, -beta, -alpha)
                board.pop()
                score = -score
                if not bestmove or score > bestscore:
                    bestscore = score
                    bestmove = [m] + nextmoves
                if score > alpha:
                    alpha = score

                if bestscore >= beta:
                    self.inc('betacuts')
                    break
            self._cache.put(board, bestmove, depth, ply, bestscore, orig_alpha, beta)
            return bestmove, bestscore


    def __str__(self):
        return 'AlphaBetaCache(%s)' % self._maxdepth


class ABIterDeepEngine(ABCachedEngine):
    FORMAT_STAT = (
            '[depth: {depth}] score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
            'hits: {hits}, leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, maxdepth=4, ordering='eval', maxitems=50000):
        super(ABIterDeepEngine, self).__init__(maxdepth, ordering, maxitems)

    def choose(self, board: ChessBoard):
        for depth in range(1, self._maxdepth+1):
            self.initcounter()
            self._counters['depth'] = depth
            pv, score = self.search(board, depth)
            self.showstats(pv, score)
            yield pv[0]

    def __str__(self):
        return 'ABIterativeDeepening(%s)' % self._maxdepth


if __name__=="__main__":
    alphabeta = AlphaBetaEngine(maxdepth=5)
    alphabeta_cached = ABCachedEngine(maxdepth=5)

    fen = "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/2PB1N2/PP1P1PPP/RNBQK2R w kq - 0 6"
    board = ChessBoard(fen)
    fen_black = "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/2PB1N2/PP1P1PPP/RNBQK2R b kq - 0 6"
    board_black = ChessBoard(fen_black)

    # best_moves_white = alphabeta.choose(board)
    # best_moves_black = alphabeta.choose(board_black)

    best_moves_white_cached = alphabeta_cached.choose(board)
    best_moves_black_cached = alphabeta_cached.choose(board_black)

    # for m in best_moves_white:
    #     print(m)
    # for m in best_moves_black:
    #     print(m)