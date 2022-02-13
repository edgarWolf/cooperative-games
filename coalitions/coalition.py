from typing import List


class Coalition:
    """Represents a coalition in context of game theory."""

    def __init__(self, players: List[int]):
        """Creates a new instance of this class."""
        self.size = len(players)
        self.players = players


    def __repr__(self) -> str:
        """Returns a string representation of this class."""
        ret_str = f"Coalition size: {self.size}\n"
        return ret_str

