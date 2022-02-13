from typing import List
from coalitions.coalition import Coalition
from games.base_game import BaseGame

class WeightedVotingGame(BaseGame):
    def __init__(self, coalitions: List[Coalition], weights: List[int], quorum : int) -> None:
        super().__init__(coalitions)
        self.weigths = weights
        self.quorum = quorum
    
    def get_winning_coalitions(self) -> List[Coalition]:
        return None