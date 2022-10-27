from indices.power_value import PowerValue
from games.game import Game
import numpy as np

class TauValue(PowerValue):
    def compute(self, game: Game) -> list[float]:
        v = game.characteristic_function()

        # Edge case 1 player.
        if len(game.players) == 1:
            return [v[(game.players[0],)]]

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
        T = []

        # Solve linear equation, to find alpha
        coeffs = np.array([[M_diff]])
        constant = np.array([constant_diff])
        alpha = np.linalg.solve(coeffs, constant)[0]
        
        # Compute and return tau vector.
        for m_i, M_i in zip(m, M):
            t = m_i + alpha * (M_i - m_i)
            T.append(t)
            
        return T
