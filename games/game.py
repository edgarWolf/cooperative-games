import enum
from games.base_game import BaseGame
from scipy.special import binom
from scipy.optimize import linprog
from typing import List, Dict, Tuple
import numpy as np


class Game(BaseGame):
    """Represents a class for cooperative games."""

    def __init__(self, contributions: List[int]) -> None:
        """Creates a new instance of this class."""
        super().__init__(contributions)

        if any(contribution for contribution in contributions if contribution < 0):
            raise ValueError("Contributions have to be greater than or equal to 0.")

        num_players = np.log2(len(contributions) + 1)
        if not num_players.is_integer():
            raise ValueError("Invalid length of the contributions vector.")
        num_players = int(num_players)

        self._players = [i for i in range(1, num_players + 1)]
        self._coalitions = self._init_coalitions()

        if not self.__check_if_contributions_are_monotone(contributions):
            raise ValueError("Contributions have to grow monotone by coalition size.")

        self._contributions = contributions

    def __repr__(self) -> str:
        repr = super().__repr__()
        max_contribs_to_show = 32
        contribs_to_show = min(max_contribs_to_show, len(self.contributions))
        repr += "contributions = ["
        for i in range(contribs_to_show):
            if i == contribs_to_show - 1:
                repr += f"{self.contributions[i]}"
            else:
                repr += f"{self.contributions[i]}, "
        repr += "]"
        return repr

    def characteristic_function(self) -> Dict:
        """Returns the characteristic of this TU game."""
        return {coalition: contribution for coalition, contribution in zip(self.coalitions, self.contributions)}

    def get_marginal_contribution(self, coalition: Tuple, player: int) -> int:
        """Returns the marginal contribution for a player in a coalition."""

        # Parameter check
        if not coalition:
            raise ValueError("No coalition provided.")

        if not player:
            raise ValueError("No player provided.")

        if player not in coalition:
            raise ValueError("Player is not part of coalition.")

        characteristic_function = self.characteristic_function()
        coalition_payoff = characteristic_function[coalition]

        # If coalition only consists of one player, return payoff of the coalition function directly.
        if len(coalition) == 1:
            return coalition_payoff

        coalition_without_player = tuple(filter(lambda x: x != player, coalition))
        coalition_without_player_payoff = characteristic_function[coalition_without_player]

        return coalition_payoff - coalition_without_player_payoff

    def get_utopia_payoff_vector(self) -> List[float]:
        """
        Returns a list of the utopia-payoffs for all players in the game.
        The utopia-payoff M_i of a player i is defined as 
        M_i = v(N) - v(N\{i}), where
            - v denotes the characteristic function of the game.
            - N denotes the grand coalition.
        """
        N = self.coalitions[-1]
        v = self.characteristic_function()
        v_N = v[N]
        M = []
        for player in self.players:
            N_without_i = tuple(sorted(p for p in N if p != player))
            v_N_without_i = v[N_without_i] if N_without_i in v else 0
            M.append(v_N - v_N_without_i)
        return M

    def get_imputation_vertices(self) -> List[List[float]]:
        """
        Returns a matrix representing the imputation vertices of the game.
        On a input of a n-player game, a n x n matrix is being returned, each row representing a vertex of a imputation.
        A vector satisfying following two conditions is considered an imputation:
            - Pareto-efficency: sum_^{n}{j=1} u_j = v(N)
            - Individual rationality: u_j >= v({j}), for all j = 1,...,n
        where N denotes the grand coalition and v the coalition function.
        A imputation vector u is payoff vector, in which the payoffs are distributed in such a way, that the players will have a reason to join the grand coalition.
        The imputations of the game is the convex hull of the obtained imputation vertices.
        """
        v = self.characteristic_function()
        N = self.coalitions[-1]
        n = len(self.players)

        if n == 1:
            return [[v[(1),]]]

        # The bounds for the payoffs for the individual players.
        lower_bounds = [v[coalition] for coalition in self.get_one_coalitions()]
        upper_bounds = [v[N] - sum(lb for j, lb in enumerate(lower_bounds) if j != i) for i, _ in
                        enumerate(lower_bounds)]
        bounds = [(lb, ub) for lb, ub in zip(lower_bounds, upper_bounds)]

        # Calculate the impuation vertices, based on the indivdual payoffs and the efficiency constraint.
        X = []
        for i, _ in enumerate(bounds):
            x = [bound[1] if i == j else bound[0] for j, bound in enumerate(bounds)]
            if x not in X:
                X.append(x)
        return X

    def get_core_vertices(self) -> np.ndarray:
        v = self.characteristic_function()
        N = self.coalitions[-1]
        n = len(self.players)

        # Get the coalitions in between the one coalitions and the grand coalition.
        cols = self.coalitions[n:-1]

        # Initialize game constraints

        # Equality constraints.
        A_eq = [[1 for _ in range(n)]]
        b_eq = [v[N]]

        # Upper bound constraints.
        A_ub = [[-1 if (i + 1) in coalition else 0 for i in range(n)] for coalition in cols]
        b_ub = [v[c] for c in cols]

        # Get the initial bounds for each player.
        lbs = [v[c] for c in self.get_one_coalitions()]
        ubs = [v[N] - sum(lb for j, lb in enumerate(lbs) if j != i) for i, _ in enumerate(lbs)]
        bounds = [(lb, ub) for lb, ub in zip(lbs, ubs)]

        # Update bounds.

        # Upper bounds.
        new_ubs = list(reversed([v[N] - b_ub[i] for i in range(n)]))
        for i, new_ub in enumerate(new_ubs):
            bounds[i] = (bounds[i][0], new_ub)

        # Lower bounds.
        new_lbs = [max(bound[0], v[N] - sum(u for j, u in enumerate(new_ubs) if j != i)) for i, bound in
                   enumerate(bounds)]
        for i, new_lb in enumerate(new_lbs):
            bounds[i] = (new_lb, bounds[i][1])

        C = self._get_maximization_coefficients(bounds)

        return np.unique(
            [np.round(linprog(c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=bounds).x).astype(int) for c in C],
            axis=0)

    def is_convex(self):
        v = self.characteristic_function().copy()
        v[tuple()] = 0
        for i, C in enumerate(self.coalitions):
            for D in self.coalitions[i:]:
                C_set = set(C)
                D_set = set(D)
                C_union_D = C_set.union(D_set)
                C_intersection_D = C_set.intersection(D)
                C_union_D = tuple(sorted(p for p in C_union_D))
                C_intersection_D = tuple(sorted(p for p in C_intersection_D))

                if v[C_union_D] + v[C_intersection_D] < v[C] + v[D]:
                    return False
        return True

    def is_additive(self):
        v = self.characteristic_function().copy()
        v[tuple()] = 0
        for i, A, in enumerate(self.coalitions):
            for B in self.coalitions[i:]:
                A_set = set(A)
                B_set = set(B)
                A_intersection_B = A_set.intersection(B_set)

                if A_intersection_B:
                    continue

                A_union_B = A_set.union(B)
                A_union_B = tuple(sorted(p for p in A_union_B))
                if v[A] + v[B] != v[A_union_B]:
                    return False
        return True

    def _get_maximization_coefficients(self, bounds: List[Tuple]) -> np.ndarray:
        v = self.characteristic_function()
        N = self.coalitions[-1]
        C = np.diag([-1 for _ in range(len(bounds))])
        C_res = []
        # Iterate over the bounds.
        for i, bound in enumerate(bounds):
            remainder = v[N] - bound[1] - sum(b[0] for j, b in enumerate(bounds) if j != i)
            # Vertex is an imputation, we can let it untouched.
            if remainder == 0:
                C_res.append(C[i])
                continue
            # We need to maximize all other players j != i, but one player k != i
            else:
                # Update current player, to be definitely maximized.
                current_max_num = C[i][i] - 1
                c = [0 for _ in range(len(bounds))]
                c[i] = current_max_num

                # Find all other players, who should not be directly maximized.
                other_players = [index for index, val in enumerate(c) if val == 0]

                # Update all players to be maximized after player i.
                for k in other_players:
                    new_c = np.array(c).copy()
                    for p in [p for p in other_players if p != k]:
                        new_c[p] = current_max_num + 1
                    C_res.append(np.array(new_c))

        return np.array(C_res)

    def get_minimal_rights_vector(self) -> List[float]:
        """
        Returns a list representing the minimal rights vector of the game.
        The minimal rights vector consists of the maximum remainders R(S, i) for a player i in coalition S.
        The remainder R(S,i) represents the payoff player i receives in coalition S, if all other players in the coalition
        get their utopia-payoff, i.e. R(S,i) = v(S) - sum_{j in S, j != i} M_j.
        Therefore, the components of the minimal rights vector are defined as
        m_i = max_{S: i in S} R(S, i) for i = 1,...,n,
        A player i can justify a minimum payoff of m_i when joining the grand coalition.
        """
        v = self.characteristic_function()
        M = self.get_utopia_payoff_vector()
        R = []
        for i in self.players:
            S_vec = [S for S in self.coalitions if i in S]
            R_S = []
            for S in S_vec:
                v_S = v[S]
                M_j_sum = sum(M_j for index, M_j in enumerate(M) if (index + 1) != i and (index + 1) in S)
                R_s_i = v_S - M_j_sum
                R_S.append(R_s_i)
            R.append(max(R_S))
        return R

    def __check_if_contributions_are_monotone(self, contributions: List[int]) -> bool:
        """
        Checks wheter the contribution vector contains montonely growing contributions.
        We define monotonley growing contributions such that any coalition with size i, has to contribute
        a higher or equal value than a coalition with size j, j < i: Contribution(j) <= Contribution(i)
        """

        # TODO: Change this behaviour on a subset basis.
        contribs_monotone = True
        start_idx = 0
        num_players = len(self.players)
        max_contribs = []
        for i in range(1, num_players + 1):

            # The number of elements for a coalition size is determined by
            # the binomial coeffiecent of the current number of players out of the whole number of players.
            # Add start_idx to the corresponding offset.  
            end_idx = int(binom(num_players, i)) + start_idx
            contribs = contributions[start_idx:end_idx]
            max_contrib = max(contribs)

            # Check if we have already seen a larger contribution in the past, i.e. in a smaller coalition.
            if any(contrib for contrib in max_contribs if contrib > max_contrib):
                contribs_monotone = False
                break

            # Update the maximum list and update the start index.
            max_contribs.append(max_contrib)
            start_idx = end_idx
        return contribs_monotone
