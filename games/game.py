from typing import List
from games.base_game import BaseGame
from coalitions.coalition import Coalition

class Game(BaseGame):
    def __init__(self, coalitions: List[Coalition]) -> None:
        super().__init__(coalitions)