from typing import List
from games.weighted_voting_game import WeightedVotingGame
from indices.power_index import PowerIndex


class JohnstonIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> List[float]:
        """
        Returns a list of the johnston-indices for all players in the game.
        The johnston-index for a player j is defined as:
        sum_{S in VC} r_j(S), where 
            - VC denotes the critical coalitions, i.e. the coalitions with at least one pivot player.
            - r_j(S) denotes the reciprocal of the number of pivot players in S, if j is a pivot player, 0 else.
        """
        VC = game.get_pivot_players()
        johnston_indices = []
        for player in game.players:
            johnston_raw = 0
            for S, critical_players in VC.items():
                r_S = 1 / len(critical_players)
                r_j_s = r_S if player in critical_players else 0
                johnston_raw += r_j_s
            johnston_indices.append(johnston_raw)

        johnston_sum = sum(johnston_indices)
        return [raw_johnston / johnston_sum for raw_johnston in johnston_indices]