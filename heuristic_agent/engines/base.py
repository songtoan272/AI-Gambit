import time
from collections import defaultdict
from typing import List

import chess


class Engine(object):
    FORMAT_STAT = ""

    def choose(self, board):
        raise NotImplemented

    def initcounter(self):
        self._startt = time.time()
        self._counters = cnt = defaultdict(int)
        cnt['nodes'] = 0
        cnt['leaves'] = 0
        cnt['draws'] = 0
        cnt['mates'] = 0

    def inc(self, cnt):
        self._counters[cnt] += 1

    def showstats(self, pv: List[chess.Move], score: int):
        t = time.time() - self._startt
        if t:
            nps = self._counters['nodes'] / t
        else:
            nps = 0

        pv: str = ', '.join(x.uci() for x in pv)

        ctx = self._counters.copy()
        ctx['pv'] = pv
        ctx['nps'] = nps
        ctx['score'] = score
        ctx['time'] = t

        print(self.FORMAT_STAT.format(**ctx))