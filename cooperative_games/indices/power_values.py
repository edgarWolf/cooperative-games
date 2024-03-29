from abc import ABC, abstractmethod
from cooperative_games.games import Game
import math
import numpy as np


class PowerValue(ABC):
    @abstractmethod
    def compute(self, game: Game) -> np.ndarray:
        pass


class ShapleyValue(PowerValue):
    def __repr__(self):
        return "Shapley Value"

    def compute(self, game: Game) -> np.ndarray:
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
        shapley_values = np.zeros((n,))

        for i, player in enumerate(game.players):
            # Initiate with marginal contribution for player's one coalition, multiplied by the complement factorial 
            # (always n-1, since the lenght of the empty coalition is 0).
            shapley_value = v[(player,)] * math.factorial(n - 1)
            coalitions_without_player = [coalition for coalition in game.coalitions if player not in coalition]
            for C in coalitions_without_player:
                C_len = len(C)
                C_len_factorial = math.factorial(C_len)
                complement_factorial = math.factorial(n - C_len - 1)
                pivot_term = v[tuple(sorted(C + (player,)))] - v[C]
                shapley_value += C_len_factorial * complement_factorial * pivot_term
            shapley_values[i] = shapley_value / factorial_n
        return shapley_values


class BanzhafValue(PowerValue):
    def __repr__(self):
        return "Banzhaf Value"

    def compute(self, game: Game, normalized: bool = True) -> np.ndarray:
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
        K = self.__K(game) if normalized else 1 / (2 ** (len(game.players) - 1))
        marg_sums = self.__marginal_contributions_sum(game)
        return np.array([K * b for b in marg_sums])

    def __K(self, game: Game) -> float:
        """Returns the coeffient for the absolute banzhaf value."""
        N = game.coalitions[-1]
        v = game.characteristic_function()
        marg_sums = self.__marginal_contributions_sum(game)
        return v[N] / sum(marg_sums)

    def __marginal_contributions_sum(self, game: Game) -> np.ndarray:
        """Returns a list of the sum of marginal contributions for each player in the game."""
        v = game.characteristic_function()
        n = len(game.players)
        marg_sums = np.zeros((n,))
        for i, player in enumerate(game.players):
            coalitions_without_player = [coalition for coalition in game.coalitions if player not in coalition]
            marg_sum = v[(player,)] + sum(v[tuple(sorted(C + (player,)))] - v[C] for C in coalitions_without_player)
            marg_sums[i] = marg_sum
        return marg_sums


class GatelyPoint(PowerValue):
    def __repr__(self):
        return "Gatley Point"

    def compute(self, game: Game) -> np.ndarray:
        """
        Returns a list of the gately points for all players in the game.
        The gately point for a player i is defined as:
        v_i + (v(N) - sum^n_{j=1} v_j) * (M_i - v_i) / (sum^n_{j=1}M_j - sum^n_{j=1} v_j), where
            - N denotes the grand coalition.
            - n denotes the number of players in the game.
            - v denotes the characteristic function of the game.
            - M denotes the utopia payoff vector.
        The Gately-point can be interpretated as the intersection of the imputationn set with the line constructed by
        the payoffs of the one-coalitions and the utopia-payoff-vector.
        """
        v = game.characteristic_function()
        N = game.coalitions[-1]
        M = game.get_utopia_payoff_vector()
        n = len(game.players)

        if len(game.players) == 1:
            return np.array([v[(game.players[0],)]])

        X = np.zeros((n,))
        for i, player in enumerate(game.players):
            v_i = v[(player,)]
            M_i = M[player - 1]
            sum_v_j = sum(v[j] for j in game.get_one_coalitions())
            N_one_coalitions_diff = v[N] - sum_v_j
            player_loss = M_i - v_i
            common_loss = sum(M) - sum_v_j
            x_i = v_i + N_one_coalitions_diff * (player_loss / common_loss)
            X[i] = x_i
        return X


class TauValue(PowerValue):
    def __repr__(self):
        return "Tau Value"

    def compute(self, game: Game) -> np.ndarray:
        """
        Returns a list of the tau Values for all players in the game.
        The tau value for a player i is defined as:
        tau_i =  alpha * m_i + (1 - alpha) * M_i, where
            - m denotes the minimal rights vector.
            - M denotes the utopia payoff vector.
            - alpha defines a value in [0, 1].
        The value of alpha is explicit defined by the constraint
        sum^n_{j=1} tau_j = v(N)
        The tau-value can be interpretated as the intersection of the imputationn set with the line constructed by
        the minimal-rights-vector and the utopia-payoff-vector.
        """
        v = game.characteristic_function()
        n = len(game.players)

        # Edge case 1 player.
        if n == 1:
            return np.array([v[(game.players[0],)]])

        N = game.coalitions[-1]
        m = game.get_minimal_rights_vector()
        M = game.get_utopia_payoff_vector()

        sum_m = sum(m)
        sum_M = sum(M)
        M_diff = sum_m - sum_M
        constant_diff = v[N] - sum_M

        # If either marginal contribution or utopia payoff vector sum are 0, alpha does not need to be complemented.
        if sum_m == 0:
            M_diff = sum_M
            constant_diff = v[N]
        elif sum_M == 0:
            M_diff = sum_m
            constant_diff = v[N]

        # Solve linear equation, to find alpha
        coeffs = np.array([[M_diff]])
        constant = np.array([constant_diff])
        alpha = np.linalg.solve(coeffs, constant)[0]

        # Compute and return tau vector.
        return np.array([m_i + alpha * (M_i - m_i) for m_i, M_i in zip(m, M)])


