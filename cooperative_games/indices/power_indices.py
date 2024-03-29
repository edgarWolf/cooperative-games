from abc import ABC, abstractmethod
import math
from typing import List, Tuple
from cooperative_games.games import WeightedVotingGame
import numpy as np


class PowerIndex(ABC):
    @abstractmethod
    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        pass


class ShapleyShubikIndex(PowerIndex):

    def __repr__(self) -> str:
        return "Shapley-Shubik Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
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
        shapley_shubik_indices = np.zeros((n,))

        # Consider edge case with only 1 player. 
        # In that case, there exists no other coalition than the coalition consisting of that one player.
        # The loop would not be triggered, such that the return value would be 0 in every execution.
        # Because of this, return just the value of the characteristic function, since it also represents the shapley-shubik-index in this case. 
        if n == 1:
            return np.array([v[(1,)]])

        for i, player in enumerate(game.players):
            shapley_shubik_index = 0
            coalitions_without_player = [coalition for coalition in game.coalitions if player not in coalition]
            for C in coalitions_without_player:
                C_len = len(C)
                C_len_factorial = math.factorial(C_len)
                complement_factorial = math.factorial(n - C_len - 1)
                # Create a sorted tuple out of the union with the current player, since the key tuples of the characterstic function are sensitive to order.
                pivot_term = v[tuple(sorted(C + (player,)))] - v[C]
                shapley_shubik_index += C_len_factorial * complement_factorial * pivot_term
            shapley_shubik_indices[i] = shapley_shubik_index / factorial_n
        return shapley_shubik_indices


class BanzhafIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Banzhaf Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a list of the banzhaf-indices for all players in the game.
        The banzhaf-index for a player j is defined as:
        sum_{C subseteq N, j not in C}  (v(C union {j}) - v(C))) / (sum^{n}_{k=1} sum_{C subseteq N, k not in C} (v(C union {k}) - v(C)))), where 
            - N denotes the grand coalition.
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
        """
        v = game.characteristic_function()
        n = len(game.players)
        banzhaf_indices = np.zeros((n,))

        # Consider edge case with only 1 player. 
        # In that case, there exists no other coalition than the coalition consisting of that one player.
        # The loop would not be triggered, such that the return value would be 0 in every execution.
        # Because of this, return just the value of the characteristic function, since it also represents the shapley-shubik-index in this case. 
        if len(game.players) == 1:
            return np.array([v[(1,)]])

        for i, player in enumerate(game.players):
            coalitions_without_player = [coalition for coalition in game.coalitions if player not in coalition]
            banzhaf_index = sum(v[tuple(sorted(C + (player,)))] - v[C] for C in coalitions_without_player)
            banzhaf_indices[i] = banzhaf_index
        banzhaf_index_sum = np.sum(banzhaf_indices)

        relative_banzhaf_indices = np.array([raw_banzhaf / banzhaf_index_sum for raw_banzhaf in banzhaf_indices])
        return relative_banzhaf_indices


class ShiftIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Shift Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a list of the shift-indices for all players in the game.
        The shift-index for a player j is defined as:
        |W^sm_j| / sum^n_k=1 |W^sm_k|, where 
            - W^sm_j denotes the set of shift minimal coalitions, where player j is a member.
        """
        W_sm = game.get_shift_winning_coalitions()
        n = len(game.players)
        W_sm_lens = np.zeros((n,))
        for i, player in enumerate(game.players):
            W_sm_j = [W for W in W_sm if player in W]
            W_sm_lens[i] = len(W_sm_j)

        W_sm_len_sum = np.sum(W_sm_lens)
        return np.array([W_len / W_sm_len_sum for W_len in W_sm_lens])


class PublicGoodIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Public-Good Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a list of the public good index for all players in the game.
        The public good index for a player j is defined as:
        |W^m_j| / sum^{n}_{k=1} |W^m_k|, where
            - W^m_j denotes all minimal winning coalitions j belongs to.
        """
        W_m = game.get_minimal_winning_coalitions()
        W_m_len = len(W_m)
        n = len(game.players)
        pgi_list = np.zeros((n,))
        for i, player in enumerate(game.players):
            W_m_j = [coalition for coalition in W_m if player in coalition]
            pgi_list[i] = len(W_m_j) / W_m_len

        pgi_sum = np.sum(pgi_list)
        return np.array([pgi / pgi_sum for pgi in pgi_list])


class PublicHelpIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Public-Help Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a list of the public help index for all players in the game.
        The public help index for a player j is defined as:
        |W_j| / sum^{n}_{k=1} |W_k|, where
            - W_j denotes all winning coalitions j belongs to.
        """
        W = game.get_winning_coalitions()
        W_len = len(W)
        n = len(game.players)
        phi_list = np.zeros((n,))
        for i, player in enumerate(game.players):
            W_j = [coalition for coalition in W if player in coalition]
            phi_list[i] = len(W_j) / W_len

        phi_sum = np.sum(phi_list)
        return np.array([phi / phi_sum for phi in phi_list])


class JohnstonIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Johnston Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a list of the johnston-indices for all players in the game.
        The johnston-index for a player j is defined as:
        sum_{S in VC} r_j(S), where 
            - VC denotes the critical coalitions, i.e. the coalitions with at least one pivot player.
            - r_j(S) denotes the reciprocal of the number of pivot players in S, if j is a pivot player, 0 else.
        """
        VC = game.get_pivot_players()
        n = len(game.players)
        johnston_indices = np.zeros((n,))
        for i, player in enumerate(game.players):
            johnston_raw = 0
            for S, critical_players in VC.items():
                num_critical_players = len(critical_players)
                if num_critical_players == 0:
                    continue
                r_S = 1 / num_critical_players
                r_j_s = r_S if player in critical_players else 0
                johnston_raw += r_j_s
            johnston_indices[i] = johnston_raw

        johnston_sum = np.sum(johnston_indices)
        return np.array([raw_johnston / johnston_sum for raw_johnston in johnston_indices])


class EgalitarianIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Egalitarian Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a  list of the egalitarian indices for all players in the game.
        The egalitarian index for a player j is defined as:
        e_i(v) = 1 / n, if v contains winning coalitions, else 0, where
            - v denotes the chararcteristic function of the game.
            - n denotes the number of players in the game.
        """
        n = len(game.players)
        winning = len(game.get_winning_coalitions()) > 0
        return np.full((n,), 1 / n) if winning else np.zeros((n,))


class GnMinusIndex(PowerIndex):
    def __repr__(self) -> str:
        return "GnMinus Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a list of the g^{n-} indices for all players in the game.
        The g^{n-} index is defined as:
        g^{n-}_i(v) = |W^{n-}_i| / sum_{j in N} |W^{n-}_j|, if |W^{n-}_j| > 0, else 0, where
            - v denotes the characteristic function of the game.
            - W^{n-}_i denotes the set of null player free coalitions containing player i.
            - N denotes the grand coalition.
        """
        null_player_free_cols = game.winning_coalitions_without_null_players()
        n = len(game.players)
        G = np.zeros((n,))
        col_lens_without_null_player = [len([col for col in null_player_free_cols if p in col]) for p in game.players]
        sum_lens_cols_without_null = sum(l_c for l_c in col_lens_without_null_player)
        if sum_lens_cols_without_null == 0:
            return np.zeros((n,))
        for i, player in enumerate(game.players):
            cols_with_player_len = len([col for col in null_player_free_cols if player in col])
            G[i] = cols_with_player_len / sum_lens_cols_without_null
        return G


class NevisonIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Nevison Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a list of the nevison indices for all players in the game.
        The nevison index is defined as:
        Z_i(v) = |W_i| / 2^{n-1}, where
            - v denotes the characteristic function of the game.
            - n denotes the number of players.
            - W_i denotes the set of winning coalitions containing player i.
        A normalized version of this index is equal to the public help index.
        """
        n = len(game.players)
        W = game.get_winning_coalitions()
        NI = np.zeros((n,))
        denominator = 2 ** (n - 1)
        for i, player in enumerate(game.players):
            W_i_len = len([c for c in W if player in c])
            NI[i] = W_i_len / denominator
        return NI


class KoenigAndBraeuningerIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Koenig-and-Braeuninger Index"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a list of the koenig-and-braeuninger indices for all players in the game.
        The koenig-and-braeuninger index is defined as:
        KB_i(v) = |W_i| / |W|, where
            - v denotes the characteristic function of the game.
            - W_i denotes the set of winning coalitions containg player i.
            - W denotes the set of winning coalitions.
        A normalized version of this index is equal to the public help index.
        """
        W = game.get_winning_coalitions()
        W_len = len(W)
        n = len(game.players)
        if W_len == 0:
            return np.zeros((n,))
        KB = np.zeros((n,))
        for i, player in enumerate(game.players):
            W_i_len = len([c for c in W if player in c])
            KB[i] = W_i_len / W_len
        return KB


class RaeIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Rae Index"

    def compute(self, game: WeightedVotingGame, normalized: bool = True) -> np.ndarray:
        """
        Returns a list of the rae indices for all players in the game.
        The rae index is defined as:
        R_i(v) = 1 / 2 + (2|W_i| - |W|) / 2^n, where
            - v denotes the characteristic function of the game.
            - n denotes the number of players in the game.
            - W_i denotes the set of winning coalitions containg player i.
            - W denotes the set of winning coalitions.
        """
        W = game.get_winning_coalitions()
        W_len = len(W)
        n = len(game.players)
        denominator = 2 ** n
        R = np.zeros((n,))
        for i, player in enumerate(game.players):
            W_i_len = len([col for col in W if player in col])
            term = (2 * W_i_len - W_len) / denominator
            R[i] = (1 / 2) + term
        if normalized:
            R_sum = np.sum(R)
            R = np.array([r / R_sum for r in R])
        return R


class SolidarityValue(PowerIndex):
    def __repr__(self) -> str:
        return "Solidarity Value"

    def compute(self, game: WeightedVotingGame) -> np.ndarray:
        """
        Returns a list of the solidarity values for all players in the game.
        The solidarity value is defined as:
        Psi_i(v) = sum_{T subseteq N, i in T} ((n - |T|)! (|T| - 1)!) / n! * A^v(T), where
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
            - N denotes the grand coalition.
            - A^v(T) denotes the average marinal contribution of a member of a coalition T,i.e
                - A^v(T) = (sum_{j in T} (v(T) - v(T \ {j})) / |T|
        """
        n = len(game.players)
        denominator = math.factorial(n)
        S = np.zeros((n,))
        for i, player in enumerate(game.players):
            coalitions_with_player = [col for col in game.coalitions if player in col]
            t = 0
            for col in coalitions_with_player:
                T_len = len(col)
                numerator = math.factorial(n - T_len) * math.factorial(T_len - 1)
                term = numerator / denominator
                A = self._A(game=game, T=col)
                t += term * A
            S[i] = t
        return S

    def _A(self, game: WeightedVotingGame, T: Tuple) -> float:
        """Returns the average marginal contribution of a member of coalition T."""
        v = game.characteristic_function().copy()
        v[tuple()] = 0
        T_len = len(T)
        A = 0
        for j in T:
            T_without_j = tuple(sorted(p for p in T if p != j))
            A += v[T] - v[T_without_j]
        return A / T_len


class HollerIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Holler Index"

    def compute(self, game: WeightedVotingGame, normalized: bool = True) -> np.ndarray:
        """
        Returns a list of the holler indices for all players in the game.
        The holler index is defined as:
        X_i(v) = | W^m_i |, where
            - v denotes the characteristic function of the game.
            - W^m_i denotes the set of minmal winning coalitions containing player i.
        """
        W_min = game.get_minimal_winning_coalitions()
        n = len(game.players)
        H = np.array([len([w for w in W_min if i in w]) for i in game.players])
        if normalized:
            H_sum = np.sum(H)
            H = np.array([h / H_sum for h in H] if H_sum > 0 else np.zeros((n,)))
        return H


class DeeganPackelIndex(PowerIndex):
    def __repr__(self) -> str:
        return "Deegan-Packel Index"

    def compute(self, game: WeightedVotingGame, normalized: bool = True) -> np.ndarray:
        """
        Returns a list of the Deegan-Packel indices for all players in the game.
        The Deegan-Packel index is defined as:
        delta_i(v) = sum_{S in W^m_i} 1 / |S|, where
            - v denotes the characteristic function of the game.
            - W^m_i denotes the set of minmal winning coalitions containing player i.
        """
        W_min = game.get_minimal_winning_coalitions()
        n = len(game.players)
        S = np.array([sum((1 / len(S)) if len(S) > 0 else 0 for S in W_min if i in S) for i in game.players])
        if normalized:
            W_min_len = len(W_min)
            if W_min_len == 0:
                return np.zeros((n,))
            normalization_term = 1 / W_min_len
            S = np.array([normalization_term * s for s in S])
        return S
