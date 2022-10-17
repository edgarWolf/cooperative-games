from typing import List
from games.weighted_voting_game import WeightedVotingGame
from indices.power_index import PowerIndex


class PublicGoodIndex(PowerIndex):
    def __init__(self, game: WeightedVotingGame) -> None:
        super().__init__(game)
    
    def compute(self) -> List[float]:
        """
        Returns a list of the public good index for all players in the game.
        The public good index for a player j is defined as:
        |W^m_j| / sum^{n}_{k=1} |W^m_k|, where
            - W^m_j denotes all minimal winning coalitions j belongs to.
        """
        W_m = self.game.get_minimal_winning_coalitions()
        W_m_len = len(W_m)
        pgi_list = []
        for player in self.game.players:
            W_m_j = [coalition for coalition in W_m if player in coalition]
            pgi_list.append(len(W_m_j) / W_m_len)
        pgi_sum = sum(pgi_list)
        return [pgi / pgi_sum for pgi in pgi_list]