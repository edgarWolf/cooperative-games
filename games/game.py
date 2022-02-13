from typing import List
from coalitions.coalition import Coalition
from games.base_game import BaseGame

class Game(BaseGame):

    def __init__(self, players: List[int]) -> None:
        super().__init__(players)
 



