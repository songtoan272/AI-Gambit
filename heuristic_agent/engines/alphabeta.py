from heuristic_agent.env.board import ChessBoard
from heuristic_agent.env.eval import INF
from heuristic_agent.engines.negamax import NegamaxEngine
from heuristic_agent.enhancements.moveordering import MoveOrdering


class AlphaBetaEngine(NegamaxEngine):
    FORMAT_STAT = (

            'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
            'leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, maxdepth=2, ordering='seq'):
        super().__init__(maxdepth)
        self.moveorder = MoveOrdering(ordering)
        self.order = self.moveorder.order

    def initcounter(self):
        super(AlphaBetaEngine, self).initcounter()
        self._counters['betacuts'] = 0

    def search(self, board: ChessBoard, depth, ply=0, alpha=-INF, beta=INF):
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
            # return [], self.quiesce(board, alpha, beta)
            return [], self.evaluate(board)

        bestmove = []
        bestscore = -INF - 1
        for m in self.order(board):
            board.push(m)
            nextmoves, score = self.search(board, depth - 1, ply + 1, -beta, -alpha)
            board.pop()
            score = -score
            if not bestmove or score > bestscore:
                bestscore = score
                bestmove = [m] + nextmoves
            if score > alpha:
                alpha = score

            if alpha >= beta:
                self.inc('betacuts')
                break

        return bestmove, alpha

    def quiesce(self, board, alpha: int, beta: int) -> int:
        # https://www.chessprogramming.org/Quiescence_Search
        stand_pat = self.evaluate(board)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        for move in board.moves:
            if board.is_capture(move):
                board.push(move)
                score = -self.quiesce(board, -beta, -alpha)
                board.pop()
                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score
        return alpha

    def __str__(self):
        return 'AlphaBeta(%s)' % self._maxdepth






