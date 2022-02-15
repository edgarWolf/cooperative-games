from typing import List, Tuple
from games.base_game import BaseGame
import math

class Game(BaseGame):
    """Represents a class for cooperative games."""

    def __init__(self, num_players: int, contributions: List[int]) -> None:
        """Creates a new instance of this class."""
        super().__init__(num_players)
        if len(contributions) != len(self.coalitions):
            raise ValueError("Vector of contributions does not match length of coalition vector.")

        if any(contribution for contribution in contributions if contribution < 1):
            raise ValueError("Contributions have to be greater than or equal to 1.")

        # TODO : Check wether contributions grow when coalition size grows.
        self.contributions = contributions


    def characteristic_function(self) -> List[Tuple]:
        """Returns the characteristic of this TU game."""
        return [(coalition, self.contributions[i]) for i, coalition in enumerate(self.coalitions)]





