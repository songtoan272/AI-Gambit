import random
from functools import partial

from heuristic_agent.evaluate import Evaluator
from heuristic_agent.board import ChessBoard


class MoveOrder(object):
    def __init__(self, name='eval'):
        if name == 'seq':
            self._order = self._order_seq
        elif name == 'random':
            self._order = self._order_random
        elif name == 'eval':
            self._order = self._order_eval
        # elif name == 'diff':
        #     self._order = self._order_diff
        else:
            raise NotImplemented()

    def _order_seq(self, board: ChessBoard):
        return board.moves

    def _order_random(self, board: ChessBoard):
        moves = board.moves
        random.shuffle(moves)
        return moves

    def _order_eval(self, board: ChessBoard):
        if not hasattr(self, 'evaluate'):
            self.evaluate = Evaluator().evaluate
        moves = board.moves
        if len(moves) <= 1:
            return moves

        return sorted(moves,
                      key=lambda m: -self.evaluate(board.move(m)),
                      reverse=True)

    # def _order_diff(self, board, moves):
    #     if len(moves) <= 1:
    #         return moves
    #
    #     return sorted(moves, key=partial(evaldiff, board),
    #                   reverse=True)

    def order(self, board):
        return self._order(board)
