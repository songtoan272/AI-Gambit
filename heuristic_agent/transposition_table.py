from collections import namedtuple, OrderedDict
from enum import Enum
from typing import List, Tuple

import chess

from heuristic_agent.board import ChessBoard
from heuristic_agent.evaluate import INF
import pickle

Entry = namedtuple('Entry', 'move depth score flag')


class Flag(Enum):
    NONE = 0
    LOWERBOUND = 1
    EXACT = 2
    UPPERBOUND = 3


class TranspositionTable:

    def __init__(self, maxitems=500000):
        self._maxitems = maxitems
        self._cache = OrderedDict()

    def put(self,
            board: ChessBoard,
            moves: List[chess.Move],
            depth: int,
            ply: int,
            score: int,
            alpha=-INF,
            beta=INF):
        """
        Put an search entry into the transition table
        :param board: The board to insert into the table
        :param moves: The moves on PV-Nodes
        :param depth: the depth searched for this node
        :param score: The returned score of this node
        :param alpha: The lowerbound for this node
        :param beta: The upperbound for this node
        :return:
        """
        key = board.hashkey
        if moves:
            move = moves[0]
        else:
            move = None

        if depth == 0 or alpha < score < beta:
            flag = Flag.EXACT
        elif score >= beta:
            flag = Flag.LOWERBOUND
            score = beta
        elif score <= alpha:
            flag = Flag.UPPERBOUND
            score = alpha
        else:
            assert False

        entry = Entry(move, depth, score, flag)
        old_entry = self._cache.get(key, None)
        if not old_entry or old_entry.depth < entry.depth:
            self._cache[key] = entry

        if len(self._cache) > self._maxitems:
            self._cache.popitem(last=False)

    def lookup(self,
               board: ChessBoard,
               depth: int,
               ply: int,
               alpha=-INF,
               beta=INF) -> Tuple[bool, chess.Move, int]:
        key = board.hashkey
        if key not in self._cache:
            return False, chess.Move.null(), 0

        entry = self._cache[key]

        hit = False
        score = 0

        if entry.depth >= depth:
            if entry.flag is Flag.EXACT:
                hit = True
                score = entry.score
            elif entry.flag is Flag.LOWERBOUND and entry.score >= beta:
                hit = True
                score = beta
            elif entry.flag is Flag.UPPERBOUND and entry.score <= alpha:
                hit = True
                score = alpha

        move = entry.move

        return hit, move, score

    def retrieve(self, board):
        key = board.hashkey
        return self._cache.get(key, None)


if __name__=="__main__":
    tt = TranspositionTable()
    tt.put(ChessBoard(), [chess.Move.null()], 0, 1, 0)
    p = pickle.dumps(tt)
    load_tt = pickle.loads(p)
    print(load_tt.lookup(ChessBoard(), 1, 0))