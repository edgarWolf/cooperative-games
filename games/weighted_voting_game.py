from typing import List
from coalitions.coalition import Coalition
from games.base_game import BaseGame

class WeightedVotingGame(BaseGame):
    def __init__(self, players: List[int], weights: List[int], quorum : int) -> None:
        super().__init__(players)
        if (len(weights) != len(players)):
            raise ValueError("Length of player vector and weight vector don't match.")
        self.weigths = weights
        self.quorum = quorum
    
    def get_winning_coalitions(self) -> List[Coalition]:
        winning_coalitions = []
        for coalition in self.coaltions:
            current_quorum = sum(self.weigths[player - 1] for player in coalition)
            if current_quorum >= self.quorum:
                winning_coalitions.append(coalition)
        return winning_coalitions