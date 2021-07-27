import random

import chess
from chess import Move
from typing import List, Tuple

from heuristic_agent.enhancements.killer_moves import KillerMoves
from heuristic_agent.env.eval import INF, evaluate
from heuristic_agent.env.board import ChessBoard
from heuristic_agent.enhancements.transposition_table import TranspositionTable


class MoveOrdering(object):
    def __init__(self, name='seq', tt: TranspositionTable=None, km: KillerMoves=None):
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
        self._tt = tt
        self._km = km
    
    def set_tt(self, tt: TranspositionTable):
        self._tt = tt
    
    def set_km(self, km: KillerMoves):
        self._km = km

    def _order_seq(self, board: ChessBoard, ply: int):
        return board.moves

    def _order_random(self, board: ChessBoard, ply: int):
        moves = board.moves
        random.shuffle(moves)
        return moves

    def _order_eval(self, board: ChessBoard, ply: int):
        if not hasattr(self, 'evaluate'):
            self.evaluate = evaluate
        moves = board.moves
        if len(moves) <= 1:
            return moves
        # inefficacy, do not use
        return sorted(moves,
                      key=lambda m: -self.evaluate(board.move(m)),
                      reverse=True)

    def _order_cache(self, board: ChessBoard, ply: int):
        ttEntry = None if self._tt is None else self._tt.retrieve(board)
        hash_move = None if not ttEntry else ttEntry.move
        captures, non_captures = self.categorize_moves(board, hash_move)
        captures = self.sort_mvv_lva(board, captures)
        non_captures = self.sort_killer_moves(non_captures, ply)
        if hash_move:
            return [hash_move] + captures + non_captures
        else:
            return captures + non_captures


    def order(self, board, ply=0) -> List[Move]:
        return self._order(board, ply=ply)

    def categorize_moves(self, board: ChessBoard, hash_move: Move):
        """
        Sort legal moves in order PV-Move - Hash Move -> captures -> non-captures
        :param hash_move:
        :param board:
        :return: Tuple(PV-Move, MVV_LVA, Killer Moves)
        """
        captures = []
        non_captures = []
        for m in board.moves:
            if m != hash_move:
                if board.is_capture(m):
                    captures.append(m)
                else:
                    non_captures.append(m)
        return captures, non_captures


    def sort_mvv_lva(self, board: ChessBoard, capture_moves: List[Move]):
        MVV_LVA_SCORE = [
            [0, 0, 0, 0, 0, 0, 0],          #victim None, attacker K, Q, R, B, N, P, None
            [10, 11, 12, 13, 14, 15, 0],    #victim P, attacker K, Q, R, B, N, P, None
            [20, 21, 22, 23, 24, 25, 0],    #victim N, attacker K, Q, R, B, N, P, None
            [30, 31, 32, 33, 34, 35, 0],    #victim B, attacker K, Q, R, B, N, P, None
            [40, 41, 42, 43, 44, 45, 0],    #victim R, attacker K, Q, R, B, N, P, None
            [50, 51, 52, 53, 54, 55, 0],    #victim Q, attacker K, Q, R, B, N, P, None
            [60, 60, 60, 60, 60, 60, 60]    #victim K, attacker K, Q, R, B, N, P, None
        ]
        res = {}
        for m in capture_moves:
            try:
                res[m] = MVV_LVA_SCORE[board.piece_at(m.to_square).piece_type][board.piece_at(m.from_square).piece_type]
            except AttributeError:
                if board.is_en_passant(m):
                    victim = board.ep_square + 8 if not board.turn else board.ep_square - 8
                    res[m] = MVV_LVA_SCORE[board.piece_at(victim).piece_type][board.piece_at(m.from_square).piece_type]
        return sorted(res, key=res.get, reverse=True)

    def sort_killer_moves(self, non_captures: List[Move], ply: int):
        killers = []
        non_killers = []
        for i in range(len(non_captures)):
            if self._km.is_killer(non_captures[i], ply):
                killers.append(non_captures[i])
            else:
                non_killers.append(non_captures[i])
        killers += non_killers
        return killers
