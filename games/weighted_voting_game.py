from typing import List, Tuple, Dict
from games.base_game import BaseGame

class WeightedVotingGame(BaseGame):
    """
    Represents the class of weighted voting games. Each coalition with a sum of weights greater than or equal to the quorum are considered winning coalitions, losing otherwise.
    """
    def __init__(self, num_players: int, weights: List[int], quorum : int) -> None:
        """Creates a new instance of this class."""
        super().__init__(num_players)

        # Parameter check.
        if len(weights) != num_players:
            raise ValueError("Length of player vector and weight vector don't match.")
        if any(weight  for weight  in weights  if weight  < 0):
            raise ValueError("Weight vector containns nonallowed negative weights.")
        if quorum < 0:
            raise ValueError("Qurom is only allowed to be greater than 0.")

        self.weigths = weights
        self.quorum = quorum

    def characteristic_function(self) -> Dict:
        """Returns the characteristic function of this weighted voting game."""
        return { coalition :  1 if sum(self.weigths[player - 1] for player in coalition) >= self.quorum else 0 for coalition in self.coalitions }


    def shapley_value(self) -> List[int]:
        return None

    def get_winning_coalitions(self) -> List[Tuple]:
        """Returns a list containing winning coalitions, i.e all coalitions with a sum of weights >= the quorum."""
        return [coalition for coalition in self.coalitions if sum(self.weigths[player - 1] for player in coalition) >= self.quorum]


    def get_pivot_players(self) -> Dict:
        """
        Returns a list with all critical players with respect to every winning coalition. 
        A player p is considered as pivot player in a winning coalition C if C becomes a losing coalition if p leaves C.
        """
        winning_coalitions = self.get_winning_coalitions()
        return { winning_coaliton : 
                [player for player in winning_coaliton if  ( sum(self.weigths[winning_player - 1] for winning_player in winning_coaliton) - self.weigths[player - 1] ) < self.quorum ] 
                for winning_coaliton in winning_coalitions }
            
