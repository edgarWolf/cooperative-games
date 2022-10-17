import math
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


    def shapley_shubik_index(self) -> List[float]:
        """
        Returns a list of the shapely-shubik-indices for all players in the game.
        The shapley-shubik-index for a player j is defined as:
        sum_{C subseteq N, j not in C} (|C|! * (n - |C| - 1)! * (v(C union {j}) - v(C))) / n!, where 
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
        """
        n = len(self.players)
        v = self.characteristic_function()
        shapley_shubik_indices = []
        for player in self.players:
            shapley_shubik_index = 0
            coalitions_without_player = [coalition for coalition in self.coalitions if player not in coalition]
            for C in coalitions_without_player:
                C_len = len(C)
                C_len_factorial = math.factorial(C_len)
                complement_factorial = math.factorial(n - C_len - 1)
                pivot_term = v[tuple( sorted( C + (player,) ) )] - v[C]
                shapley_shubik_index += C_len_factorial * complement_factorial * pivot_term
            shapley_shubik_indices.append(shapley_shubik_index / math.factorial(n))
        return shapley_shubik_indices


    def get_winning_coalitions(self) -> List[Tuple]:
        """Returns a list containing winning coalitions, i.e all coalitions with a sum of weights >= the quorum."""
        return [coalition for coalition in self.coalitions if sum(self.weigths[player - 1] for player in coalition) >= self.quorum]


    def get_pivot_players(self, all_coalitions=False) -> Dict:
        """
        Returns a list with all critical players with respect to every winning coalition. 
        A player p is considered as pivot player in a winning coalition C if C becomes a losing coalition if p leaves C.
        """
        winning_coalitions = self.get_winning_coalitions()

        if all_coalitions:
            return { coalition : 
                                [player for player in coalition if  ( sum(self.weigths[winning_player - 1] for winning_player in coalition) - self.weigths[player - 1] ) < self.quorum and coalition in winning_coalitions ] 
                                for coalition in self.coalitions }
        else:
            return { winning_coaliton : 
                    [player for player in winning_coaliton if  ( sum(self.weigths[winning_player - 1] for winning_player in winning_coaliton) - self.weigths[player - 1] ) < self.quorum ] 
                    for winning_coaliton in winning_coalitions }
            
