from typing import List, Deque
from collections import deque
from chess import Move


class KillerMoves:
    def __init__(self, depth, nb_moves_store: int):
        self.nb_slots = nb_moves_store
        self.depth = depth
        self.killers: List[Deque[Move]] = [deque([Move.null() for _ in range(self.nb_slots)])
                                           for _ in range(self.depth+1)]

    def insert_killer(self, move: Move, ply: int):
        if self.is_killer(move, ply):
            return
        if not self.killers[ply][0]:
            self.killers[ply][0] = move
        else:
            self.killers[ply].rotate(1)
            self.killers[ply][0] = move

    def get_killers(self, ply: int):
        # return self.killers[ply]
        for km in self.killers[ply]:
            yield km

    def is_killer(self, move: Move, ply: int):
        return move in self.killers[ply]
