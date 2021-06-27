from heuristic_agent.engines.negamax import NegamaxEngine
from heuristic_agent.evaluate import INF
from heuristic_agent.moveorder import MoveOrder


class AlphaBetaEngine(NegamaxEngine):
    FORMAT_STAT = (
            'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
            'leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, maxdepth=2, ordering='seq'):
        super(AlphaBetaEngine, self).__init__(maxdepth)
        self.moveorder = MoveOrder(ordering).order

    def initcounter(self):
        super(AlphaBetaEngine, self).initcounter()
        self._counters['betacuts'] = 0

    def search(self, board, depth, ply=1, alpha=-INF, beta=INF):
        self.inc('nodes')

        if board.end is not None:
            return self.endscore(board, ply)

        if depth <= 0:
            self.inc('leaves')
            return [], self.quiesce(board, alpha, beta)

        bestmove = []
        bestscore = alpha
        for m in self.moveorder(board):
            board.push(m)
            nextmoves, score = self.search(board, depth - 1, ply + 1, -beta, -bestscore)
            board.pop()
            score = -score
            if score > bestscore:
                bestscore = score
                bestmove = [m] + nextmoves
            elif not bestmove:
                bestmove = [m] + nextmoves

            if bestscore >= beta:
                self.inc('betacuts')
                break

        return bestmove, bestscore

    def quiesce(self, board, alpha, beta):
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