from typing import List
from games.weighted_voting_game import WeightedVotingGame
from indices.power_index import PowerIndex


class PublicHelpIndex(PowerIndex):
    def __init__(self, game: WeightedVotingGame) -> None:
        super().__init__(game=game)

    def compute(self) -> List[float]:
        """
        Returns a list of the public help index for all players in the game.
        The public help index for a player j is defined as:
        |W_j| / sum^{n}_{k=1} |W_k|, where
            - W_j denotes all winning coalitions j belongs to.
        """
        W = self.game.get_winning_coalitions()
        W_len = len(W)
        phi_list = []
        for player in self.game.players:
            W_j = [coalition for coalition in W if player in coalition]
            phi_list.append(len(W_j) / W_len)
        phi_sum = sum(phi_list)
        return [phi / phi_sum for phi in phi_list]
