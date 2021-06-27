import chess


class ChessBoard(chess.Board):
    def __init__(self, *args):
        super().__init__(*args)

    @property
    def moves(self):
        return self.legal_moves

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
