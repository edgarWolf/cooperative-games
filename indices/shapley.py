import math
from games.weighted_voting_game import WeightedVotingGame
from games.game import Game
from indices.power_value import PowerValue
from indices.power_index import PowerIndex

class ShapleyValue(PowerValue):
    def compute(self, game: Game) -> list[float]:
        """
        Returns a list of the shapley values for all players in the game.
        The shapley value for a player j is defined as:
        sum_{C subseteq N, j not in C} (|C|! * (n - |C| - 1)! * (v(C union {j}) - v(C))) / n!, where 
            - N denotes the grand coalition.
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
        """
        n = len(game.players)
        factorial_n = math.factorial(n)
        v = game.characteristic_function()
        shapley_values = []

        for player in game.players:
            # Initiate with marginal contribution for player's one coalition, multiplied by the complement factorial 
            # (always n-1, since the lenght of the empty coalition is 0).
            shapley_value = v[(player,)] * math.factorial(n - 1)
            coalitions_without_player = [coalition for coalition in game.coalitions if player not in coalition]
            for C in coalitions_without_player:
                C_len = len(C)
                C_len_factorial = math.factorial(C_len)
                complement_factorial = math.factorial(n - C_len - 1)
                pivot_term = v[tuple( sorted( C + (player,) ) )] - v[C]
                shapley_value += C_len_factorial * complement_factorial * pivot_term
            shapley_values.append(shapley_value / factorial_n)
        return shapley_values

        




class ShapleyShubikIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> list[float]:
        """
        Returns a list of the shapley-shubik-indices for all players in the game.
        The shapley-shubik-index for a player j is defined as:
        sum_{C subseteq N, j not in C} (|C|! * (n - |C| - 1)! * (v(C union {j}) - v(C))) / n!, where 
            - N denotes the grand coalition.
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
        """
        n = len(game.players)
        factorial_n = math.factorial(n)
        v = game.characteristic_function()
        shapley_shubik_indices = []

        # Consider edge case with only 1 player. 
        # In that case, there exists no other coalition than the coalition consisting of that one player.
        # The loop would not be triggered, such that the return value would be 0 in every execution.
        # Because of this, return just the value of the characteristic function, since it also represents the shapley-shubik-index in this case. 
        if n == 1:
            return [v[(1,)]]

        for player in game.players:
            shapley_shubik_index = 0
            coalitions_without_player = [coalition for coalition in game.coalitions if player not in coalition]
            for C in coalitions_without_player:
                C_len = len(C)
                C_len_factorial = math.factorial(C_len)
                complement_factorial = math.factorial(n - C_len - 1)
                # Create a sorted tuple out of the union with the current player, since the key tuples of the characterstic function are sensitive to order.
                pivot_term = v[tuple( sorted( C + (player,) ) )] - v[C]
                shapley_shubik_index += C_len_factorial * complement_factorial * pivot_term
            shapley_shubik_indices.append(shapley_shubik_index / factorial_n)
        return shapley_shubik_indices