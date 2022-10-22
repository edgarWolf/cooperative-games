from indices.power_index import PowerIndex
from games.weighted_voting_game import WeightedVotingGame

class ShiftIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> list[float]:
        """
        Returns a list of the shift-indices for all players in the game.
        The shift-index for a player j is defined as:
        |W^sm_j| / sum^n_k=1 |W^sm_k|, where 
            - W^sm_j denotes the set of shift minimal coalitions, where player j is a member.
        """
        W_sm = game.get_shift_winning_coalitions()
        W_sm_lens = []
        for player in game.players:
            W_sm_j = [W for W in W_sm if player in W]
            W_sm_lens.append(len(W_sm_j))
        
        W_sm_len_sum = sum(W_sm_lens)
        return [W_len / W_sm_len_sum for W_len in W_sm_lens]

        


