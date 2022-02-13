from typing import List, Tuple
from coalitions.coalition import Coalition
from games.base_game import BaseGame

class WeightedVotingGame(BaseGame):
    """
    Represents the class of weighted voting games. Each coalition with a sum of weights greater than or equal to the quorum are considered winning coalitions, losing otherwise.
    """
    def __init__(self, players: List[int], weights: List[int], quorum : int) -> None:
        """Creates a new instance of this class."""
        super().__init__(players)
        if (len(weights) != len(players)):
            raise ValueError("Length of player vector and weight vector don't match.")
        self.weigths = weights
        self.quorum = quorum
    
    def get_winning_coalitions(self) -> List[Coalition]:
        """Returns a list containing winning coalitions, i.e all coalitions with a weight >= the quorum."""
        winning_coalitions = []
        for coalition in self.coalitions:
            current_quorum = sum(self.weigths[player - 1] for player in coalition)
            if current_quorum >= self.quorum:
                winning_coalitions.append(coalition)
        return winning_coalitions


    def get_pivot_players(self) -> List[Tuple[Coalition, List[int]]]:
        """
        Returns a list with all critical players with respect to every winning coalition. 
        A player p is considered as pivot player in a winning coalition C if C becomes a losing coalition if p leaves C.
        """
        pivots = []
        winning_coalitions = self.get_winning_coalitions()
        for i, winning_coalition in enumerate(winning_coalitions):
            pivots.append((winning_coalition, []))
            for player in winning_coalition:
                current_quorum = sum(self.weigths[player - 1] for player in winning_coalition)
                reduced_quorum = current_quorum - self.weigths[player - 1]
                if reduced_quorum < self.quorum:
                    pivots[i][1].append(player)
        return pivots
            
