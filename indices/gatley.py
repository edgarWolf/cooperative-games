from indices.power_value import PowerValue
from games.game import Game


class GatelyPoint(PowerValue):
    def compute(self, game: Game) -> list[float]:
        v = game.characteristic_function()
        N = game.coalitions[-1]
        M = game.get_utopia_payoff_vector()

        if len(game.players) == 1:
            return [v[(game.players[0],)]]

        X = []
        for player in game.players:
            v_i = v[(player,)]
            M_i = M[player - 1]
            sum_v_j = sum(v[j] for j in game.get_one_coalitions())
            N_one_coalitions_diff = v[N] - sum_v_j
            player_loss = M_i - v_i
            common_loss = sum(M) - sum_v_j
            x_i = v_i + N_one_coalitions_diff * (player_loss / common_loss)
            X.append(x_i)
        return X