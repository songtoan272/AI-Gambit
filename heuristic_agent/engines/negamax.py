import time
from collections import defaultdict

from heuristic_agent.evaluate import INF
from heuristic_agent.engines.greedy import GreedyEngine


class NegamaxEngine(GreedyEngine):
    FORMAT_STAT = (
            'score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, maxdepth=4):
        super(NegamaxEngine, self).__init__()
        self._maxdepth = int(maxdepth)

    def choose(self, board):
        self.initcounter()
        pv, score = self.search(board, self._maxdepth)

        self.showstats(pv, score)

        return pv[0]

    def initcounter(self):
        self._startt = time.time()
        self._counters = cnt = defaultdict(int)
        cnt['nodes'] = 0
        cnt['leaves'] = 0
        cnt['draws'] = 0
        cnt['mates'] = 0

    def inc(self, cnt):
        self._counters[cnt] += 1

    def showstats(self, pv, score):
        t = time.time() - self._startt
        if t:
            nps = self._counters['nodes'] / t
        else:
            nps = 0

        pv = ', '.join(x.uci() for x in pv)

        ctx = self._counters.copy()
        ctx['pv'] = pv
        ctx['nps'] = nps
        ctx['score'] = score
        ctx['time'] = t

        print(self.FORMAT_STAT.format(**ctx))

    def search(self, board, depth, ply=0):
        """
        Search best move from the current board state using negamax implementation
        :param board: representation of board
        :param depth: depth left to search
        :param ply: number of depth (half-move) already searched
        :return: sequence of moves to go from the current board to the best found and the corresponding score
        """
        self.inc('nodes')

        if board.end is not None:
            return self.endscore(board, ply)

        if depth <= 0:
            self.inc('leaves')
            return [], self.evaluate(board)

        bestmove = []
        bestscore = -INF
        for m in board.moves:
            board.push(m)
            nextmoves, score = self.search(board, depth - 1, ply + 1)
            board.pop()
            score = -score
            # print(board.fen(), score)
            if not bestmove or score >= bestscore:
                bestscore = score
                bestmove = [m] + nextmoves

        return bestmove, bestscore

    def endscore(self, board, ply):
        self.inc('leaves')
        if board.end == 0:
            self.inc('draws')
        else:
            self.inc('mates')
        return [], self.evaluate(board) - ply * (1 if board.turn else -1)

    def __str__(self):
        return 'Negamax(%s)' % self._maxdepth
