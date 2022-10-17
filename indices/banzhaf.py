from games.weighted_voting_game import WeightedVotingGame
from indices.power_value import PowerValue
from indices.power_index import PowerIndex
from typing import List

class BanzhafValue(PowerValue):
    def __init__(self) -> None:
        super.__init__()




class BanzhafIndex(PowerIndex):
    def __init__(self, game: WeightedVotingGame) -> None:
        super().__init__(game=game)
    
    def compute(self) -> List[float]:
        """
        Returns a list of the banzhaf-indices for all players in the game.
        The banzhaf-index for a player j is defined as:
        sum_{C subseteq N, j not in C}  (v(C union {j}) - v(C))) / (sum^{n}_{k=1} sum_{C subseteq N, k not in C} (v(C union {k}) - v(C)))), where 
            - N denotes the grand coalition.
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
        """
        v = self.game.characteristic_function()
        banzhaf_indices = []

        # Consider edge case with only 1 player. 
        # In that case, there exists no other coalition than the coalition consisting of that one player.
        # The loop would not be triggered, such that the return value would be 0 in every execution.
        # Because of this, return just the value of the characteristic function, since it also represents the shapley-shubik-index in this case. 
        if len(self.game.players) == 1:
            return [v[(1,)]]

        for player in self.game.players:
            coalitions_without_player = [coalition for coalition in self.game.coalitions if player not in coalition]
            banzhaf_index = sum( v[tuple( sorted( C + (player,) ) )] - v[C] for C in coalitions_without_player )
            banzhaf_indices.append(banzhaf_index)
        
        banzhaf_index_sum = sum(banzhaf_indices)
        relative_banzhaf_indices = [raw_banzhaf / banzhaf_index_sum for raw_banzhaf in banzhaf_indices]
        return relative_banzhaf_indices