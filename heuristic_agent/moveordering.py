import random
from functools import partial

import chess
from typing import List

from heuristic_agent.evaluate import Evaluator, INF
from heuristic_agent.board import ChessBoard
from heuristic_agent.transposition_table import TranspositionTable


class MoveOrdering(object):
    def __init__(self, name='eval'):
        if name == 'seq':
            self._order = self._order_seq
        elif name == 'random':
            self._order = self._order_random
        elif name == 'eval':
            self._order = self._order_eval
        elif name == 'cache':
            self._order = self._order_cache
        else:
            raise NotImplemented()

    def _order_seq(self, board: ChessBoard, cached=None):
        return board.moves

    def _order_random(self, board: ChessBoard, cached=None):
        moves = board.moves
        random.shuffle(moves)
        return moves

    def _order_eval(self, board: ChessBoard, cached=None):
        if not hasattr(self, 'evaluate'):
            self.evaluate = Evaluator().evaluate
        moves = board.moves
        if len(moves) <= 1:
            return moves

        return sorted(moves,
                      key=lambda m: -self.evaluate(board.move(m)),
                      reverse=True)

    def _order_cache(self, board: ChessBoard, cached: TranspositionTable = None):
        if not cached:
            return self._order_eval(board)
        ttEntry = cached.retrieve(board)
        if not ttEntry or ttEntry.depth == 0:
            return self._order_eval(board)
        if ttEntry.depth > 0:
            move_score = {}
            for m in board.moves:
                board.push(m)
                e = cached.retrieve(board)
                board.pop()
                if e:
                    move_score[m] = e.score
                else:
                    move_score[m] = -INF
            return sorted(move_score, key=move_score.get)

    def order(self, board, cached=None) -> List[chess.Move]:
        return self._order(board, cached)
