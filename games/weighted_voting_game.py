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
            - N denotes the grand coalition.
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
        """
        n = len(self.players)
        factorial_n = math.factorial(n)
        v = self.characteristic_function()
        shapley_shubik_indices = []

        # Consider edge case with only 1 player. 
        # In that case, there exists no other coalition than the coalition consisting of that one player.
        # The loop would not be triggered, such that the return value would be 0 in every execution.
        # Because of this, return just the value of the characteristic function, since it also represents the shapley-shubik-index in this case. 
        if n == 1:
            return [v[(1,)]]

        for player in self.players:
            shapley_shubik_index = 0
            coalitions_without_player = [coalition for coalition in self.coalitions if player not in coalition]
            for C in coalitions_without_player:
                C_len = len(C)
                C_len_factorial = math.factorial(C_len)
                complement_factorial = math.factorial(n - C_len - 1)
                # Create a sorted tuple out of the union with the current player, since the key tuples of the characterstic function are sensitive to order.
                pivot_term = v[tuple( sorted( C + (player,) ) )] - v[C]
                shapley_shubik_index += C_len_factorial * complement_factorial * pivot_term
            shapley_shubik_indices.append(shapley_shubik_index / factorial_n)
        return shapley_shubik_indices


    def banzhaf_index(self) -> List[float]:
        """
        Returns a list of the banzhaf-indices for all players in the game.
        The banzhaf-index for a player j is defined as:
        sum_{C subseteq N, j not in C}  (v(C union {j}) - v(C))) / (sum^{n}_{k=1} sum_{C subseteq N, k not in C} (v(C union {k}) - v(C)))), where 
            - N denotes the grand coalition.
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
        """
        v = self.characteristic_function()
        banzhaf_indices = []

        # Consider edge case with only 1 player. 
        # In that case, there exists no other coalition than the coalition consisting of that one player.
        # The loop would not be triggered, such that the return value would be 0 in every execution.
        # Because of this, return just the value of the characteristic function, since it also represents the shapley-shubik-index in this case. 
        if len(self.players) == 1:
            return [v[(1,)]]

        for player in self.players:
            coalitions_without_player = [coalition for coalition in self.coalitions if player not in coalition]
            banzhaf_index = sum( v[tuple( sorted( C + (player,) ) )] - v[C] for C in coalitions_without_player )
            banzhaf_indices.append(banzhaf_index)
        
        banzhaf_index_sum = sum(banzhaf_indices)
        relative_banzhaf_indices = [raw_banzhaf / banzhaf_index_sum for raw_banzhaf in banzhaf_indices]
        return relative_banzhaf_indices

    
    def johnston_index(self) -> List[float]:
        """
        Returns a list of the johnston-indices for all players in the game.
        The johnston-index for a player j is defined as:
        sum_{S in VC} r_j(S), where 
            - VC denotes the critical coalitions, i.e. the coalitions with at least one pivot player.
            - r_j(S) denotes the reciprocal of the number of pivot players in S, if j is a pivot player, 0 else.
        """
        VC = self.get_pivot_players()
        johnston_indices = []
        for player in self.players:
            johnston_raw = 0
            for S, critical_players in VC.items():
                r_S = 1 / len(critical_players)
                r_j_s = r_S if player in critical_players else 0
                johnston_raw += r_j_s
            johnston_indices.append(johnston_raw)

        johnston_sum = sum(johnston_indices)
        return [raw_johnston / johnston_sum for raw_johnston in johnston_indices]


    def get_minimal_winning_coalitions(self):
        """Returns a list of the minimal winning coalitions."""
        critical_coalitions = self.get_pivot_players()
        return [coalition for coalition, critical_players in critical_coalitions.items() if coalition == tuple(critical_players)]


    def get_winning_coalitions(self) -> List[Tuple]:
        """Returns a list containing winning coalitions, i.e all coalitions with a sum of weights >= the quorum."""
        return [coalition for coalition in self.coalitions if sum(self.weigths[player - 1] for player in coalition) >= self.quorum]


    def get_pivot_players(self, all_coalitions=False) -> Dict[Tuple, List]:
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
            
