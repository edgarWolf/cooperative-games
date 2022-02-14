from typing import List, Tuple
from games.base_game import BaseGame

class WeightedVotingGame(BaseGame):
    """
    Represents the class of weighted voting games. Each coalition with a sum of weights greater than or equal to the quorum are considered winning coalitions, losing otherwise.
    """
    def __init__(self, num_players: int, weights: List[int], quorum : int) -> None:
        """Creates a new instance of this class."""
        super().__init__(num_players)

        # Parameter check.
        if (len(weights) != num_players):
            raise ValueError("Length of player vector and weight vector don't match.")
        if any(weight  for weight  in weights  if weight  < 0):
            raise ValueError("Weight vector containns nonallowed negative weights.")
        if quorum < 0:
            raise ValueError("Qurom is only allowed to be greater than 0.")

        self.weigths = weights
        self.quorum = quorum

    def characteristic_function(self) -> List[Tuple]:
        """Returns the characteristic function of this weighted voting game."""
        return [ (coalition, 1) if sum(self.weigths[player - 1] for player in coalition) >= self.quorum else (coalition, 0)  for coalition in self.coalitions  ]


    def get_winning_coalitions(self) -> List[Tuple]:
        """Returns a list containing winning coalitions, i.e all coalitions with a weight >= the quorum."""
        winning_coalitions = []
        for coalition in self.coalitions:
            current_quorum = sum(self.weigths[player - 1] for player in coalition)
            if current_quorum >= self.quorum:
                winning_coalitions.append(coalition)
        return winning_coalitions


    def get_pivot_players(self) -> List[Tuple[Tuple, List[int]]]:
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
            
