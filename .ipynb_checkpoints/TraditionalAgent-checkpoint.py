import chess
import chess.svg
import chess.polyglot
import chess.pgn
import chess.engine


class TraditionalAgent:
    """
    This engine uses Minimax algorithm with Negamax implementation to look into all possibilities in a predefined
    number of moves in the future and choose one that yields the best score.

    The score is the evaluation of a given state of the game. Basically, it is calculated by the pieces left on
    the chessboard, each piece has its own value, and where these pieces are placed on the board, predefined by
    Piece-Square Tables.

    The engine may use some move from opening books if there are moves available for the current board.
    """

    def __init__(self, max_depth=3):
        """
        Evaluating the board using Simplified Evaluation Function explained here
        https://www.chessprogramming.org/Simplified_Evaluation_Function
        Tune the parameters pieces and PSTable to change behavior of the engine
        
        :param chess.Board board: the current board 
        :param int max_depth: max number of moves ahead to search in the tree
        :param dict pieces: the value for each type of pieces
        :param dict pstable: the Piece-Square Table, each table corresponds to a specific piece
            Each Piece-Square Table is of dim(8x8) with row index corresponds to row index of a chessboard
            The columns of a P-S Table correspond to those of a chessboard (a to h)
            Chess is about standing position and taking control of the center therefore the center usually
        """
        # self.board = board if board is not None else chess.Board()
        self.max_depth = max_depth
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

    def evaluate_board(self, board):
        # Verify if the game is still going on
        if board.is_checkmate():
            if board.turn:
                return -9999
            else:
                return 9999
        if board.is_stalemate():
            return 0
        if board.is_insufficient_material():
            return 0

        # Number of each pieces of each player
        wp = len(board.pieces(chess.PAWN, chess.WHITE))
        bp = len(board.pieces(chess.PAWN, chess.BLACK))
        wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
        bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
        wb = len(board.pieces(chess.BISHOP, chess.WHITE))

        bb = len(board.pieces(chess.BISHOP, chess.BLACK))
        wr = len(board.pieces(chess.ROOK, chess.WHITE))
        br = len(board.pieces(chess.ROOK, chess.BLACK))
        wq = len(board.pieces(chess.QUEEN, chess.WHITE))
        bq = len(board.pieces(chess.QUEEN, chess.BLACK))

        # CALCULATE SCORE
        # Material Score
        material = self.pieces['P'] * (wp - bp) + \
                   self.pieces['N'] * (wn - bn) + \
                   self.pieces['B'] * (wb - bb) + \
                   self.pieces['R'] * (wr - br) + \
                   self.pieces['Q'] * (wq - bq)
        # Individual Score
        pawnsq = sum([self.pstable['P'][i] for i in board.pieces(chess.PAWN, chess.WHITE)]) - \
                 sum([-self.pstable['P'][chess.square_mirror(i)] for i in board.pieces(chess.PAWN, chess.BLACK)])
        knightsq = sum([self.pstable['N'][i] for i in board.pieces(chess.KNIGHT, chess.WHITE)]) - \
                   sum([-self.pstable['N'][chess.square_mirror(i)] for i in
                        board.pieces(chess.KNIGHT, chess.BLACK)])
        bishopsq = sum([self.pstable['B'][i] for i in board.pieces(chess.BISHOP, chess.WHITE)]) - \
                   sum([-self.pstable['B'][chess.square_mirror(i)] for i in
                        board.pieces(chess.BISHOP, chess.BLACK)])
        rooksq = sum([self.pstable['R'][i] for i in board.pieces(chess.ROOK, chess.WHITE)]) - \
                 sum([-self.pstable['R'][chess.square_mirror(i)] for i in board.pieces(chess.ROOK, chess.BLACK)])
        queensq = sum([self.pstable['Q'][i] for i in board.pieces(chess.QUEEN, chess.WHITE)]) - \
                  sum([-self.pstable['Q'][chess.square_mirror(i)] for i in board.pieces(chess.QUEEN, chess.BLACK)])
        # Verify if the ending begins, it might be either:
        # 1. Both sides have no queens
        # 2. Every side which has a queen has additionally no other self.pieces or one minorpiece max
        if (wq == bq == 0) or (
                (wq == 1 and (wn + wb + wr == 0 or wn + wb == 1)) or (bq == 1 and (bn + bb + br == 0 or bn + bb == 1))
        ):
            kingsq = sum([self.pstable['KE'][i] for i in board.pieces(chess.KING, chess.WHITE)])
            kingsq = kingsq + sum([-self.pstable['KE'][chess.square_mirror(i)]
                                   for i in board.pieces(chess.KING, chess.BLACK)])
        else:
            kingsq = sum([self.pstable['KM'][i] for i in board.pieces(chess.KING, chess.WHITE)])
            kingsq = kingsq + sum([-self.pstable['KM'][chess.square_mirror(i)]
                                   for i in board.pieces(chess.KING, chess.BLACK)])

        eval = material + pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq
        if board.turn:
            return eval
        else:
            return -eval

    def _alphabeta(self, board, alpha, beta, depthleft):
        """
        Searching the best move using minimax with negamax implementation and
        alphabeta algorithm to reduce computation time
        https://www.chessprogramming.org/Alpha-Beta

        :param board: the chess board state to do the search from
        :param alpha: the minimum score that the maximizing player is assured of
        :param beta: the maximum score that the minimizing player is assured of
        :param depthleft: the depth of the search tree from the current search state == number of anticipated moves
        :return: the best score obtained 
        """
        bestscore = -9999
        if depthleft == 0:
            return self._quiesce(board, alpha, beta)
        for move in board.legal_moves:
            board.push(move)
            score = -self._alphabeta(board, -beta, -alpha, depthleft - 1)
            board.pop()
            if score >= beta:
                return score
            if score > bestscore:
                bestscore = score
            if score > alpha:
                alpha = score
        return bestscore

    def _quiesce(self, board, alpha, beta):
        # https://www.chessprogramming.org/Quiescence_Search
        stand_pat = self.evaluate_board(board)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        for move in board.legal_moves:
            if board.is_capture(move):
                board.push(move)
                score = -self._quiesce(board, -beta, -alpha)
                board.pop()

                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha

    @staticmethod
    def _inverse_move(move: chess.Move):
        move_uci = move.uci()
        inv_move_uci = move_uci[0] + \
                       str(9 - int(move_uci[1])) + \
                       move_uci[2] + \
                       str(9 - int(move_uci[3])) + \
                       move_uci[4:]
        return chess.Move.from_uci(inv_move_uci)

    def selectmove(self, board: chess.Board = None, player=chess.WHITE):
        board = chess.Board() if not board else board
        if not player:
            board = board.mirror()
        try:
            move = chess.polyglot.MemoryMappedReader("./opening-books/human.bin").weighted_choice(board).move
            # move = chess.polyglot.MemoryMappedReader("./opening-books/computer.bin").weighted_choice(self.board).move
            # move = chess.polyglot.MemoryMappedReader("./opening-books/pecg_book.bin").weighted_choice(self.board).move
            return move
        except:
            bestMove = chess.Move.null()
            bestValue = -99999
            alpha = -100000
            beta = 100000
            for move in board.legal_moves:
                board.push(move)
                boardValue = -self._alphabeta(board, -beta, -alpha, self.max_depth - 1)
                if boardValue > bestValue:
                    bestValue = boardValue
                    bestMove = move
                if boardValue > alpha:
                    alpha = boardValue
                board.pop()
            return bestMove if player else self._inverse_move(bestMove)


if __name__ == "__main__":
    fen = "rnbqk1nr/pppp1p1p/8/1B4p1/1b1pP3/5N2/PPP2PPP/RNBQK2R w KQkq - 2 5"
    board = chess.Board(fen)
    agent = TraditionalAgent(board)
    print(agent.selectmove())
