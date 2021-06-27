import copy

import chess
import numpy as np


class ChessGame:
    """
    Represents a chess environment where a chess game is played

    Attributes:
        :ivar chess.Board board: current board state
        :ivar Winner winner: winner of the game
        :ivar boolean resigned: whether non-winner resigned
    """

    def __init__(self, board: chess.Board=None):
        if not board:
            self.board: chess.Board = chess.Board()
        else:
            self.board: chess.Board = board
        self.winner = None

    def reset(self):
        """
        Resets to begin a new game
        :return ChessEnv: self
        """
        self.board.reset()

    def copy(self):
        env = copy.copy(self)
        env.board = copy.copy(self.board)
        return env

    @property
    def is_white_turn(self):
        return self.board.turn

    @property
    def is_ended(self):
        return self.board.is_game_over()

    @property
    def result(self):
        return ChessGame.get_game_ended(self.board)

    @property
    def actions_size(self):
        return self.get_moves().count()

    def get_moves(self):
        return self.board.legal_moves

    def move(self, action: str):
        """
        Make a move and updates the game states accordingly
        :param action: move to take in UCI notation
        :return: self
        """

        self.board.push(chess.Move.from_uci(action))

        if self.board.result(claim_draw=True) != "*":
            self._game_over()

    def retreat_move(self):
        self.board.pop()
        if self.board.result(claim_draw=True) == "*":
            self.winner = None

    def _game_over(self):
        if self.winner is None:
            result = self.board.result(claim_draw=True)
            if result == '1-0':
                self.winner = 1
            elif result == '0-1':
                self.winner = -1
            else:
                self.winner = 0

    @staticmethod
    def next_state(board: chess.Board, action: str) -> chess.Board:
        """
        Simulate the next state by making a move from the current state, the original game is not modified
        :param action: the move to realize
        :return: the next state of the current board
        """
        b = board.copy()
        b.push_uci(action)
        return b

    @staticmethod
    def get_game_ended(board: chess.Board, player=True):
        """
        Determine if the game represented by the given board is ended
        :param board: The board to evaluate
        :param player: The current player turn, default to 1 as we use canonical board
        :return: 0 if game has not ended.
                1 if player won, -1 if player lost, small non-zero value for draw.
        """
        result = board.result(claim_draw=True)
        if result == '1-0':
            return 1.0
        elif result == '0-1':
            return -1.0
        elif result == '1/2-1/2':
            return 0.0
        else:
            return None

    @staticmethod
    def is_terminal(board: chess.Board):
        result = board.result(claim_draw=True)
        return result == '1-0' or result == '0-1' or result == '1/2-1/2'

    @staticmethod
    def inverse_move(move_uci: str):
        inv_move_uci = move_uci[0] + \
                       str(9 - int(move_uci[1])) + \
                       move_uci[2] + \
                       str(9 - int(move_uci[3])) + \
                       move_uci[4:]
        return inv_move_uci

    @staticmethod
    def inverse_moves(moves: [str]):
        return [ChessGame.inverse_move(move) for move in moves]

    def __repr__(self):
        return repr("\n" + self.board.fen() + "\n")

    def string_repr(self, board=None):
        return self.board.epd() if board is None else board.epd()

    def get_canonical_board(self):
        return self.board.mirror() if self.board.turn == chess.BLACK else self.board

    def serialize(self):
        """
            Translate the current state of the game into an input array for the NN.
            Each Square of the board is represent by 4 bits.
            A case will therefore be represented by a number between 0-15.
            Each number in this range represents a specific type of piece (including castling and en passant)
            The last indexed 8x8 array represents the current player turn and the halfmoves clock
        :return: a (5*8*8) binary matrix of 0s and 1s representing the canonical form of board
                The canonical form should be independent of player. For e.g. in chess,
                the canonical form can be chosen to be from the pov of white. When the
                player is white, we can return board as is. When the player is black,
                we can invert the colors and return the board.
        """
        assert self.board.is_valid()
        # invert the board if the player is black to get the canonical form
        board = self.board if self.board.turn else self.board.mirror()

        bytes_state = np.zeros(64, np.uint8)
        for i in range(64):
            pp = board.piece_at(i)
            if pp is not None:
                bytes_state[i] = {"P": 1, "N": 2, "B": 3, "R": 4, "Q": 5, "K": 6,
                             "p": 9, "n": 10, "b": 11, "r": 12, "q": 13, "k": 14}[pp.symbol()]
        if board.has_queenside_castling_rights(chess.WHITE):
            assert bytes_state[0] == 4
            bytes_state[0] = 7
        if board.has_kingside_castling_rights(chess.WHITE):
            assert bytes_state[7] == 4
            bytes_state[7] = 7
        if board.has_queenside_castling_rights(chess.BLACK):
            assert bytes_state[56] == 8 + 4
            bytes_state[56] = 8 + 7
        if board.has_kingside_castling_rights(chess.BLACK):
            assert bytes_state[63] == 8 + 4
            bytes_state[63] = 8 + 7

        if board.ep_square is not None:
            assert bytes_state[board.ep_square] == 0
            bytes_state[board.ep_square] = 8
        bytes_state = bytes_state.reshape(8, 8)

        # binary state
        bit_state = np.zeros((5, 8, 8), np.uint8)

        # to binary
        bit_state[0] = (bytes_state >> 3) & 1
        bit_state[1] = (bytes_state >> 2) & 1
        bit_state[2] = (bytes_state >> 1) & 1
        bit_state[3] = (bytes_state >> 0) & 1

        # whose turn: all 1 if white, all 0 if black
        # bit_state[4] = (board.turn * 1.0)

        # nb of half moves
        bit_state[4] = board.halfmove_clock

        return bit_state

