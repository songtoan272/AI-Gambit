from heuristic_agent.env.board import ChessBoard
from heuristic_agent.engines.alphabeta_cached import ABCachedEngine


class ABIterDeepEngine(ABCachedEngine):
    FORMAT_STAT = (
            '[depth: {depth}] score: {score} [time: {time:0.3f}s, pv: {pv}]\n' +
            'nps: {nps}, nodes: {nodes}, betacuts: {betacuts}\n' +
            'hits: {hits}, leaves: {leaves}, draws: {draws}, mates: {mates}'
    )

    def __init__(self, maxdepth=4, ordering='cache', maxitems=1024000):
        super(ABIterDeepEngine, self).__init__(maxdepth, ordering, maxitems)

    def choose(self, board: ChessBoard):
        for depth in range(1, self._maxdepth + 1):
            self.initcounter()
            self._counters['depth'] = depth
            pv, score = self.search(board, depth)
            self.showstats(pv, score)
            yield pv[0]

    def __str__(self):
        return 'ABIterativeDeepening(max_depth=%s)' % self._maxdepth
