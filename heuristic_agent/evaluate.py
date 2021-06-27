import numpy as np
import chess

from heuristic_agent.board import ChessBoard

INF = 100000


class Evaluator(object):
    """
    Evaluate the board position and return the advantage of the side to move.
    """
    def __init__(self):
        self.pieces = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
        self.pstable = {
            "P": [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, -20, -20, 10, 10, 5,
                5, -5, -10, 0, 0, -10, -5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, 5, 10, 25, 25, 10, 5, 5,
                10, 10, 20, 30, 30, 20, 10, 10,
                50, 50, 50, 50, 50, 50, 50, 50,
                0, 0, 0, 0, 0, 0, 0, 0],

            "N": [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50],
            "B": [
                -20, -10, -10, -10, -10, -10, -10, -20,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -20, -10, -10, -10, -10, -10, -10, -20],
            "R": [
                0, 0, 0, 5, 5, 0, 0, 0,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                5, 10, 10, 10, 10, 10, 10, 5,
                0, 0, 0, 0, 0, 0, 0, 0],
            "Q": [
                -20, -10, -10, -5, -5, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 5, 5, 5, 5, 5, 0, -10,
                0, 0, 5, 5, 5, 5, 0, -5,
                -5, 0, 5, 5, 5, 5, 0, -5,
                -10, 0, 5, 5, 5, 5, 0, -10,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -20, -10, -10, -5, -5, -10, -10, -20],
            "KM": [
                20, 30, 10, 0, 0, 10, 30, 20,
                20, 20, 0, 0, 0, 0, 20, 20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30],
            "KE": [
                -50, -30, -30, -30, -30, -30, -30, -50,
                -30, -30, 0, 0, 0, 0, -30, -30,
                -30, -10, 20, 30, 30, 20, -10, -30,
                -30, -10, 30, 40, 40, 30, -10, -30,
                -30, -10, 30, 40, 40, 30, -10, -30,
                -30, -10, 20, 30, 30, 20, -10, -30,
                -30, -20, -10, 0, 0, -10, -20, -30,
                -50, -40, -30, -20, -20, -30, -40, -50]
        }

    def evaluate(self, board: ChessBoard):
        """
        Return the evaluation of the board in regard with the player turn
        :param board:
        :return:
        """
        # Verify if the game is still going on
        if board.end is not None:
            result = board.end
            if result != 0:
                if (board.end == 1 and board.turn) or (board.end == -1 and not board.turn):
                    return INF
                else:
                    return -INF
            else:
                return 0

        # Number of each pieces of each player
        wp = len(board.pieces(chess.PAWN, chess.WHITE))
        wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
        wb = len(board.pieces(chess.BISHOP, chess.WHITE))
        wr = len(board.pieces(chess.ROOK, chess.WHITE))
        wq = len(board.pieces(chess.QUEEN, chess.WHITE))

        bp = len(board.pieces(chess.PAWN, chess.BLACK))
        bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
        bb = len(board.pieces(chess.BISHOP, chess.BLACK))
        br = len(board.pieces(chess.ROOK, chess.BLACK))
        bq = len(board.pieces(chess.QUEEN, chess.BLACK))

        # CALCULATE SCORE
        # Material Score
        material = self.pieces['P'] * (wp - bp) + \
                   self.pieces['N'] * (wn - bn) + \
                   self.pieces['B'] * (wb - bb) + \
                   self.pieces['R'] * (wr - br) + \
                   self.pieces['Q'] * (wq - bq)

        # Individual Score
        pawnsq = sum([self.pstable['P'][i] for i in board.pieces(chess.PAWN, chess.WHITE)]) + \
                 sum([-self.pstable['P'][chess.square_mirror(i)] for i in board.pieces(chess.PAWN, chess.BLACK)])
        knightsq = sum([self.pstable['N'][i] for i in board.pieces(chess.KNIGHT, chess.WHITE)]) - \
                   sum([-self.pstable['N'][chess.square_mirror(i)] for i in
                        board.pieces(chess.KNIGHT, chess.BLACK)])
        bishopsq = sum([self.pstable['B'][i] for i in board.pieces(chess.BISHOP, chess.WHITE)]) + \
                   sum([-self.pstable['B'][chess.square_mirror(i)] for i in
                        board.pieces(chess.BISHOP, chess.BLACK)])
        rooksq = sum([self.pstable['R'][i] for i in board.pieces(chess.ROOK, chess.WHITE)]) + \
                 sum([-self.pstable['R'][chess.square_mirror(i)] for i in board.pieces(chess.ROOK, chess.BLACK)])
        queensq = sum([self.pstable['Q'][i] for i in board.pieces(chess.QUEEN, chess.WHITE)]) + \
                  sum([-self.pstable['Q'][chess.square_mirror(i)] for i in board.pieces(chess.QUEEN, chess.BLACK)])

        # Verify if the ending begins, it might be either:
        # 1. Both sides have no queens
        # 2. Every side which has a queen has additionally no other self.pieces or one minorpiece max
        if (wq == bq == 0) or (
                (wq == 1 and (wn + wb + wr == 0 or wn + wb == 1)) or
                (bq == 1 and (bn + bb + br == 0 or bn + bb == 1))
        ):
            kingsq = sum([self.pstable['KE'][i] for i in board.pieces(chess.KING, chess.WHITE)]) + \
                     sum([-self.pstable['KE'][chess.square_mirror(i)] for i in board.pieces(chess.KING, chess.BLACK)])
        else:
            kingsq = sum([self.pstable['KM'][i] for i in board.pieces(chess.KING, chess.WHITE)]) + \
                     sum([-self.pstable['KM'][chess.square_mirror(i)] for i in board.pieces(chess.KING, chess.BLACK)])

        eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
        return eval if board.turn else -eval

if __name__ == "__main__":
    fen = "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/2PB1N2/PP1P1PPP/RNBQK2R w kq - 0 6"
    board = ChessBoard(fen)
    fen_black = "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/2PB1N2/PP1P1PPP/RNBQK2R b kq - 0 6"
    board_black = ChessBoard(fen_black)

    eval = Evaluator()
    print(eval.evaluate(board))
    print(eval.evaluate(board_black))