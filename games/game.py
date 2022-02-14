from typing import List
from games.base_game import BaseGame

class Game(BaseGame):
    """Represents a class for cooperative games."""

    def __init__(self, players: List[int]) -> None:
        """Creates a new instance of this class."""
        super().__init__(players)
 



