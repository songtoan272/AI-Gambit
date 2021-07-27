import chess
from chess import Move

from heuristic_agent.env.board import ChessBoard


INF = 100000

pieces = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
pstable = {
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

score_diff_mid_kingside_castling = -pstable['KM'][chess.E4] - pstable['R'][chess.H1] + pstable['KM'][chess.G1] + pstable['R'][chess.F1]
score_diff_mid_queenside_castling = -pstable['KM'][chess.E4] - pstable['R'][chess.A1] + pstable['KM'][chess.C1] + pstable['R'][chess.D1]
score_diff_end_kingside_castling = -pstable['KE'][chess.E4] - pstable['R'][chess.H1] + pstable['KE'][chess.G1] + pstable['R'][chess.F1]
score_diff_end_queenside_castling = -pstable['KE'][chess.E4] - pstable['R'][chess.A1] + pstable['KE'][chess.C1] + pstable['R'][chess.D1]



def evaluate_white(board: ChessBoard) -> int:
    """
    Return the evaluation of the board in regard with the player turn
    :param board:
    :return:
    """
    # Verify if the game is still going on
    if board.end is not None:
        result = board.end
        if result != 0:
            return INF * result
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
    material = pieces['P'] * (wp - bp) + \
               pieces['N'] * (wn - bn) + \
               pieces['B'] * (wb - bb) + \
               pieces['R'] * (wr - br) + \
               pieces['Q'] * (wq - bq)

    # Individual Score
    pawnsq = sum([pstable['P'][i] for i in board.pieces(chess.PAWN, chess.WHITE)]) + \
             sum([-pstable['P'][chess.square_mirror(i)] for i in board.pieces(chess.PAWN, chess.BLACK)])
    knightsq = sum([pstable['N'][i] for i in board.pieces(chess.KNIGHT, chess.WHITE)]) - \
               sum([-pstable['N'][chess.square_mirror(i)] for i in
                    board.pieces(chess.KNIGHT, chess.BLACK)])
    bishopsq = sum([pstable['B'][i] for i in board.pieces(chess.BISHOP, chess.WHITE)]) + \
               sum([-pstable['B'][chess.square_mirror(i)] for i in
                    board.pieces(chess.BISHOP, chess.BLACK)])
    rooksq = sum([pstable['R'][i] for i in board.pieces(chess.ROOK, chess.WHITE)]) + \
             sum([-pstable['R'][chess.square_mirror(i)] for i in board.pieces(chess.ROOK, chess.BLACK)])
    queensq = sum([pstable['Q'][i] for i in board.pieces(chess.QUEEN, chess.WHITE)]) + \
              sum([-pstable['Q'][chess.square_mirror(i)] for i in board.pieces(chess.QUEEN, chess.BLACK)])

    # Verify if the ending begins, it might be either:
    # 1. Both sides have no queens
    # 2. Every side which has a queen has additionally no other pieces or one minorpiece max
    if (wq == bq == 0) or (
            (wq == 1 and (wn + wb + wr == 0 or wn + wb == 1)) or
            (bq == 1 and (bn + bb + br == 0 or bn + bb == 1))
    ):
        kingsq = sum([pstable['KE'][i] for i in board.pieces(chess.KING, chess.WHITE)]) + \
                 sum([-pstable['KE'][chess.square_mirror(i)] for i in board.pieces(chess.KING, chess.BLACK)])
    else:
        kingsq = sum([pstable['KM'][i] for i in board.pieces(chess.KING, chess.WHITE)]) + \
                 sum([-pstable['KM'][chess.square_mirror(i)] for i in board.pieces(chess.KING, chess.BLACK)])

    eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
    return eval


def evaluate(board: ChessBoard):
    eval = evaluate_white(board)
    eval = eval if board.turn else -eval
    board.score = eval
    return eval


def eval_from_move(board: ChessBoard, move: Move):
    move_piece = board.piece_at(move.from_square).symbol()
    if board.is_capture(move):
        if board.is_en_passant(move):
            victim_sq = board.ep_square + 8 if not board.turn else board.ep_square - 8
            victim_piece = board.piece_at(victim_sq).symbol()



