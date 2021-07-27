from heuristic_agent.engines.base import Engine
from heuristic_agent.env.eval import evaluate_white, INF
from heuristic_agent.env.board import ChessBoard


class MinimaxEngine(Engine):
    FORMAT_STAT = (
            'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, max_depth):
        self._maxdepth = max_depth
        self.evaluate = evaluate_white

    def min_level(self, board: ChessBoard, depth: int):
        self.inc('nodes')
        if board.end is not None:
            self.inc('leaves')
            if board.end == 0:
                self.inc('draws')
            else:
                self.inc('mates')
            return [], self.evaluate(board)

        if depth <= 0:
            self.inc('leaves')
            return [], self.evaluate(board)

        bestscore = INF+1
        bestmove = []
        for m in board.moves:
            board.push(m)
            moves, score = self.max_level(board, depth-1)
            board.pop()
            if not bestmove or score < bestscore:
                bestscore = score
                bestmove = [m] + moves
        return bestmove, bestscore

    def max_level(self, board: ChessBoard, depth:int):
        self.inc('nodes')
        if board.end is not None:
            self.inc('leaves')
            if board.end == 0:
                self.inc('draws')
            else:
                self.inc('mates')
            return [], self.evaluate(board)

        if depth <= 0:
            self.inc('leaves')
            return [], self.evaluate(board)

        bestscore = -INF-1
        bestmove = []
        for m in board.moves:
            board.push(m)
            moves, score = self.min_level(board, depth-1)
            board.pop()
            if not bestmove or score > bestscore:
                bestscore = score
                bestmove = [m] + moves
        return bestmove, bestscore

    def search(self, board:ChessBoard, depth:int):
        if board.turn:
            return self.max_level(board, depth)
        else:
            return self.min_level(board, depth)

    def choose(self, board):
        self.initcounter()
        pv, score = self.search(board, self._maxdepth)

        self.showstats(pv, score)

        return pv[0]


if __name__=="__main__":
    fen = "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/2PB1N2/PP1P1PPP/RNBQK2R w kq - 0 6"
    board = ChessBoard(fen)
    fen_black = "rnbqkb1r/pp2pppp/3p1n2/2p5/4P3/2PB1N2/PP1P1PPP/RNBQK2R b kq - 0 6"
    board_black = ChessBoard(fen_black)

    agent = MinimaxEngine(3)
    white_move = agent.choose(board)
    black_move = agent.choose(board_black)

