from abc import ABC, abstractmethod
import math
from typing import List
from games.weighted_voting_game import WeightedVotingGame


class PowerIndex(ABC):
    @abstractmethod
    def compute(self, game: WeightedVotingGame) -> List[float]:
        pass


class ShapleyShubikIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> List[float]:
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
                pivot_term = v[tuple(sorted(C + (player,)))] - v[C]
                shapley_shubik_index += C_len_factorial * complement_factorial * pivot_term
            shapley_shubik_indices.append(shapley_shubik_index / factorial_n)
        return shapley_shubik_indices


class BanzhafIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> List[float]:
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
            banzhaf_index = sum(v[tuple(sorted(C + (player,)))] - v[C] for C in coalitions_without_player)
            banzhaf_indices.append(banzhaf_index)

        banzhaf_index_sum = sum(banzhaf_indices)
        relative_banzhaf_indices = [raw_banzhaf / banzhaf_index_sum for raw_banzhaf in banzhaf_indices]
        return relative_banzhaf_indices


class ShiftIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> List[float]:
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


class PublicGoodIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> List[float]:
        """
        Returns a list of the public good index for all players in the game.
        The public good index for a player j is defined as:
        |W^m_j| / sum^{n}_{k=1} |W^m_k|, where
            - W^m_j denotes all minimal winning coalitions j belongs to.
        """
        W_m = game.get_minimal_winning_coalitions()
        W_m_len = len(W_m)
        pgi_list = []
        for player in game.players:
            W_m_j = [coalition for coalition in W_m if player in coalition]
            pgi_list.append(len(W_m_j) / W_m_len)
        pgi_sum = sum(pgi_list)
        return [pgi / pgi_sum for pgi in pgi_list]


class PublicHelpIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> List[float]:
        """
        Returns a list of the public help index for all players in the game.
        The public help index for a player j is defined as:
        |W_j| / sum^{n}_{k=1} |W_k|, where
            - W_j denotes all winning coalitions j belongs to.
        """
        W = game.get_winning_coalitions()
        W_len = len(W)
        phi_list = []
        for player in game.players:
            W_j = [coalition for coalition in W if player in coalition]
            phi_list.append(len(W_j) / W_len)
        phi_sum = sum(phi_list)
        return [phi / phi_sum for phi in phi_list]


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


class EgalitarianIndex(PowerIndex):
    def compute(self, game: WeightedVotingGame) -> List[float]:
        """
        Returns a  list of the egalitarian indices for all players in the game.
        The egalitarian index for a player j is defined as:
        e_i(v) = 1 / n, if v contains winning coalitions, else 0, where
            - v denotes the chararcteristic function of the game.
            - n denotes the number of players in the game.
        """
        n = len(game.players)
        winning = len(game.get_winning_coalitions()) > 0
        return [1 / n for _ in range(n)] if winning else [0 for _ in range(n)]


class GnMinusIndex(PowerIndex):

    def compute(self, game: WeightedVotingGame) -> List[float]:
        """
        Returns a list of the g^{n-} indices for all players in the game.
        The g^{n-} index is defined as:
        g^{n-}_i(v) = |W^{n-}_i| / sum_{j in N} |W^{n-}_j|, if |W^{n-}_j| > 0, else 0, where
            - v denotes the characteristic function of the game.
            - W^{n-}_i denotes the set of null player free coalitions containing player i.
            - N denotes the grand coalition.
        """
        null_player_free_cols = game.winning_coalitions_without_null_players()
        G = []
        col_lens_without_null_player = [len([col for col in null_player_free_cols if p in col]) for p in game.players]

        for player in game.players:
            cols_with_player_len = len([col for col in null_player_free_cols if player in col])
            sum_lens_other_cols = sum(l_c for l_c in col_lens_without_null_player)
            if sum_lens_other_cols == 0:
                G.append(0)
            else:
                G.append(cols_with_player_len / sum_lens_other_cols)
        return G