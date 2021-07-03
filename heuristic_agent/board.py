from typing import List

import chess
from chess.polyglot import zobrist_hash


class ChessBoard(chess.Board):
    def __init__(self, *args):
        super().__init__(*args)

    @property
    def moves(self) -> List[chess.Move]:
        return list(self.legal_moves)

    @property
    def hashkey(self):
        return zobrist_hash(self)

    def move(self, move: chess.Move):
        b = self.copy()
        b.push(move)
        return b

    def unmove(self):
        b = self.copy()
        b.pop()
        return b

    @property
    def end(self):
        result = self.result(claim_draw=True)
        if result == '1-0':
            return 1
        elif result == '0-1':
            return -1
        elif result == '1/2-1/2':
            return 0
        else:
            return None

