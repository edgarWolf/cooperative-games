from typing import List


class Coalition:
    def __init__(self, players: List[int]):
        self.size = len(players)
        self.players = players


    def __repr__(self) -> str:
        ret_str = f"Coalition size: {self.size}\n"
        return ret_str

