from numbers import Real
from games.weighted_voting_game import WeightedVotingGame
from games.game import Game
from indices.power_value import PowerValue
from indices.power_index import PowerIndex

class BanzhafValue(PowerValue):
    def compute(self, game: Game, normalized=True) -> list[float]:
        """
        Returns a list of the banzhaf-values for all players in the game.
        The banzhaf-value can be defined as an absolute value, and a relative value.
        The absolute value is generally not efficient, i.e. the values don't generally add up to the payoff of the grand coalition, while the relative value does.
        The absolute value for a player j is defined as:
        1/(2^{n-1}) sum_{C subseteq N, j not in C} (v(C union {j}) - v(C)), where 
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
        The relative value is defined as:
        K sum_{C subseteq N, j not in C} (v(C union {j}) - v(C)), where
            - K = v(N) / sum^n_{j=1} sum_{C subseteq N, j not in C} (v(C union {j}) - v(C)).
        """
        K = self.__K(game) if normalized else 1 / (2**(len(game.players) - 1))
        marg_sums = self.__marginal_contributions_sum(game)
        return list(map(lambda b: K * b, marg_sums))


    def __K(self, game: Game) -> float:
        """Returns the coeffient for the absolute banzhaf value."""
        N = game.coalitions[-1]
        v = game.characteristic_function()
        marg_sums = self.__marginal_contributions_sum(game)
        return v[N] / sum(marg_sums)
    
    def __marginal_contributions_sum(self, game: Game) -> list[Real]:
        """Returns a list of the sum of marginal contributions for each player in the game."""
        v = game.characteristic_function()
        marg_sums = []
        for player in game.players:
            coalitions_without_player = [coalition for coalition in game.coalitions if player not in coalition]
            marg_sum = v[(player,)] + sum( v[tuple(sorted(C + (player,)))] - v[C] for C in coalitions_without_player )
            marg_sums.append(marg_sum)
        return marg_sums

        

class BanzhafIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> list[float]:
        """
        Returns a list of the banzhaf-indices for all players in the game.
        The banzhaf-index for a player j is defined as:
        sum_{C subseteq N, j not in C}  (v(C union {j}) - v(C))) / (sum^{n}_{k=1} sum_{C subseteq N, k not in C} (v(C union {k}) - v(C)))), where 
            - N denotes the grand coalition.
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
        """
        v = game.characteristic_function()
        banzhaf_indices = []

        # Consider edge case with only 1 player. 
        # In that case, there exists no other coalition than the coalition consisting of that one player.
        # The loop would not be triggered, such that the return value would be 0 in every execution.
        # Because of this, return just the value of the characteristic function, since it also represents the shapley-shubik-index in this case. 
        if len(game.players) == 1:
            return [v[(1,)]]

        for player in game.players:
            coalitions_without_player = [coalition for coalition in game.coalitions if player not in coalition]
            banzhaf_index = sum( v[tuple( sorted( C + (player,) ) )] - v[C] for C in coalitions_without_player )
            banzhaf_indices.append(banzhaf_index)
        
        banzhaf_index_sum = sum(banzhaf_indices)
        relative_banzhaf_indices = [raw_banzhaf / banzhaf_index_sum for raw_banzhaf in banzhaf_indices]
        return relative_banzhaf_indices