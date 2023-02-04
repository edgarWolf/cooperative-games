from abc import ABC, abstractmethod
from itertools import chain, combinations
from typing import List, Dict, Tuple, Optional
import numpy as np
from scipy.optimize import linprog
from scipy.special import binom


class BaseGame(ABC):
    """
    Represents a base class for games in context of game theory.
    """

    def __init__(self, contributions: List[int]) -> None:
        """Base constructor for all derived classes."""
        if not contributions:
            raise ValueError("No contributions provided.")

        self._players = []
        self._coalitions = []
        self._contributions = []

    def __repr__(self) -> str:
        num_players = len(self.players)
        if num_players == 1:
            return "1 player game\n"
        return f"{len(self.players)} players game\n"

    @property
    def players(self) -> List[int]:
        """Property for players field."""
        return self._players

    @property
    def coalitions(self) -> List[Tuple]:
        """Property for coalitions field."""
        return self._coalitions

    @property
    def contributions(self) -> List[int]:
        """Property for contributions field."""
        return self._contributions

    @abstractmethod
    def characteristic_function(self) -> Dict[Tuple, int]:
        """Returns the characteristic function of the game."""
        pass

    def _init_coalitions(self) -> List[Tuple]:
        """Returns all possible coalitions based on the player vector of the current game."""
        powerset = self.__powerset(self.players)
        return powerset

    def __powerset(self, elements: List) -> List[Tuple]:
        """Returns the powerset from a given list."""
        return list(chain.from_iterable(combinations(elements, r) for r in range(1, len(elements) + 1)))

    def get_one_coalitions(self) -> List[tuple]:
        """Returns a list of one coalitions exisiting in the current game."""
        return [coalition for coalition in self.coalitions if len(coalition) == 1]


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

    def get_utopia_payoff_vector(self) -> np.ndarray:
        """
        Returns a list of the utopia-payoffs for all players in the game.
        The utopia-payoff M_i of a player i is defined as
        M_i = v(N) - v(N\{i}), where
            - v denotes the characteristic function of the game.
            - N denotes the grand coalition.
        """
        N = self.coalitions[-1]
        v = self.characteristic_function()
        n = len(self.players)
        v_N = v[N]
        M = np.zeros((n,))
        for i, player in enumerate(self.players):
            N_without_i = tuple(sorted(p for p in N if p != player))
            v_N_without_i = v[N_without_i] if N_without_i in v else 0
            M[i] = v_N - v_N_without_i
        return M

    def _get_core_bounds(self) -> List[Tuple]:
        v = self.characteristic_function()
        N = self.coalitions[-1]
        lower_bounds = [v[coalition] for coalition in self.get_one_coalitions()]
        upper_bounds = [v[N] - sum(lb for j, lb in enumerate(lower_bounds) if j != i) for i, _ in
                        enumerate(lower_bounds)]
        return [(lb, ub) for lb, ub in zip(lower_bounds, upper_bounds)]

    def is_in_imputation_set(self, x) -> bool:
        """
        Checks wheter a given vector is in the imputation set.
        """
        if len(x) != len(self.players):
            raise ValueError("Input vector's length does not match the number of players in the game.")
        N = self.coalitions[-1]
        v = self.characteristic_function()
        v_N = v[N]
        v_one_coalitions = [v[c] for c in self.get_one_coalitions()]
        # Check if point lies within the range and for pareto efficiency.
        return all([lb <= p for p, lb in zip(x, v_one_coalitions)]) and sum(x) == v_N

    def is_in_core(self, x) -> bool:
        """
        Checks wheter a given vector is in the core..
        """
        if len(x) != len(self.players):
            raise ValueError("Input vector's length does not match the number of players in the game.")
        N = self.coalitions[-1]
        v_N = self.characteristic_function()[N]
        bounds = self._get_core_bounds()
        # Check if point lies within the range and for pareto efficiency.
        return all([lb <= p <= ub for p, (lb, ub) in zip(x, bounds)]) and sum(x) == v_N

    def get_imputation_vertices(self) -> np.ndarray:
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
        n = len(self.players)

        if n == 1:
            return np.array([[v[(1),]]])

        # The bounds for the payoffs for the individual players.
        bounds = self._get_core_bounds()

        # Calculate the impuation vertices, based on the indivdual payoffs and the efficiency constraint.
        X = np.zeros((n, n))
        for i, _ in enumerate(bounds):
            x = [bound[1] if i == j else bound[0] for j, bound in enumerate(bounds)]
            X[i] = x

        # Remove duplicate vectors.
        X = np.unique(X, axis=0)
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

    def is_convex(self) -> bool:
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

    def is_additive(self) -> bool:
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

    def get_minimal_rights_vector(self) -> np.ndarray:
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
        n = len(self.players)
        R = np.zeros((n,))
        for i, player in enumerate(self.players):
            S_vec = [S for S in self.coalitions if player in S]
            R_S = np.zeros((len(S_vec),))
            for j, S in enumerate(S_vec):
                v_S = v[S]
                M_j_sum = np.sum(M_j for index, M_j in enumerate(M) if (index + 1) != player and (index + 1) in S)
                R_s_i = v_S - M_j_sum
                R_S[j] = R_s_i
            R[i] = np.max(R_S)
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


class WeightedVotingGame(BaseGame):
    """
    Represents the class of weighted voting games. Each coalition with a sum of weights greater than or equal to the quorum are considered winning coalitions, losing otherwise.
    """

    def __init__(self, contributions: List[int], quorum: int) -> None:
        """Creates a new instance of this class."""
        super().__init__(contributions)

        num_players = len(contributions)
        self._players = [i for i in range(1, num_players + 1)]
        self._coalitions = self._init_coalitions()

        # Parameter check.
        if any(weight for weight in contributions if weight < 0):
            raise ValueError("Weight vector containns nonallowed negative weights.")
        if quorum < 0:
            raise ValueError("Qurom is only allowed to be greater than 0.")

        self._contributions = contributions
        self.quorum = quorum

    def __repr__(self) -> str:
        repr = super().__repr__()
        repr += f"quorum = {self.quorum}"
        repr += "\n"
        max_weights_to_show = 32
        weights_to_show = min(max_weights_to_show, len(self.contributions))
        repr += "weights = ["
        for i in range(weights_to_show):
            if i == weights_to_show - 1:
                repr += f"{self.contributions[i]}"
            else:
                repr += f"{self.contributions[i]}, "
        repr += "]"
        return repr

    def characteristic_function(self) -> Dict[Tuple, int]:
        """Returns the characteristic function of this weighted voting game."""
        return {coalition: 1 if sum(self.contributions[player - 1] for player in coalition) >= self.quorum else 0 for
                coalition in self.coalitions}

    def null_players(self) -> List[int]:
        """
        Returns a list of null players in the game.
        A player i is considered a null player, if i never becomes a pivot player, i.e.
        forall S in P(N) v(S union {i}) - v(S) = 0, where
            - v denotes the characteristic function of the game.
            - N dentes the grand coalition.
            - P(N) denotes the powerset of all coalitions.
        """
        v = self.characteristic_function().copy()
        coalitions = self.coalitions.copy()
        coalitions.insert(0, tuple())
        v[tuple()] = 0
        null_players = []

        for i in self.players:
            cols = [S for S in coalitions if i not in S or S is ()]
            is_null_player = True
            for S in cols:
                S_set = set(S)
                S_union_i = S_set.union({i})
                S_union_i = tuple(sorted(p for p in S_union_i))
                if v[S_union_i] - v[S] == 1:
                    is_null_player = False
                    break
            if is_null_player:
                null_players.append(i)

        return null_players

    def winning_coalitions_without_null_players(self) -> List[Tuple]:
        """Returns a list of all winning coalitions without null players."""
        null_players = self.null_players()
        winning_coalitions = self.get_winning_coalitions()
        return [col for col in winning_coalitions if not any(p for p in col if p in null_players)]

    def get_minimal_winning_coalitions(self) -> List[Tuple]:
        """Returns a list of the minimal winning coalitions."""
        critical_coalitions = self.get_pivot_players()
        return [coalition for coalition, critical_players in critical_coalitions.items() if
                coalition == tuple(critical_players)]

    def get_winning_coalitions(self) -> List[Tuple]:
        """Returns a list containing winning coalitions, i.e all coalitions with a sum of weights >= the quorum."""
        return [coalition for coalition in self.coalitions if
                sum(self.contributions[player - 1] for player in coalition) >= self.quorum]

    def get_shift_winning_coalitions(self) -> List[Tuple]:
        """
        Returns a list containing all shift-minimal coalitions.
        A minimal winning coalition S in W_m is called shift-minimal, if it holds, that
        for every player i in S and every player j not in S with i > j, it holds:
            (S/{i}) union {j} not in W_m.
        A shift minimal winning coalition is therefore are minimal winning coalition, where no player can not be replaced by a less desired player.
        """

        W_m = self.get_minimal_winning_coalitions()
        shift_minimal_winning_coalitions = []
        unique_pivot_players = set(sum(W_m, ()))
        for S in W_m:
            is_condition_met = True
            for i in S:
                players_not_in_S = [player for player in unique_pivot_players if
                                    player not in S and self.preferred_player(i, player) == i]

                for j in players_not_in_S:
                    S_without_i = tuple(p for p in S if p != i)
                    S_without_i_union_j = tuple(sorted(S_without_i + (j,)))
                    # Found a minimal winning coalition by shifting with a less desirable player --> Not shift minimal.
                    if S_without_i_union_j in W_m:
                        is_condition_met = False
                        break

                # Break out of outer loop
                if not is_condition_met:
                    break

            if is_condition_met:
                shift_minimal_winning_coalitions.append(S)

        return shift_minimal_winning_coalitions

    def preferred_player(self, i: int, j: int, prefer_by_weight: bool = True) -> Optional[int]:
        """
        Returns the preferred player between the two players passed as parameters.
        The function is commutative, such that on input (i,j) returns i if i > j, and accordingly j on input(j,i) if j > i.
        2 conditions must be met, such that i > j:
            1): For all coalitions S subset N with i not in S and j not in S, it holds:
                (S union {j}) in W => (S union {i}) in W
            (2) There exists at least one coalition T subset N with i not in T and j not in T, such that
                (T union {j}) not in W and (T union {i}) in W.
        If both conditions are not met, j will be preferred.
        If only condition 1 is met, and preferation by weight is enabled, player i will be prefered, if w(i) > w(j), else no preferation exists.
        Otherwise, no preferation exists.
        """
        if i not in self.players or j not in self.players:
            raise ValueError("Specified players are note part of the game.")

        coalitions = self.coalitions[:-1]
        condition_one_met = True
        condition_two_met = False
        winning_coalitions = self.get_winning_coalitions()

        # Condition 1:
        S = [s for s in coalitions if i not in s and j not in s]
        for s in S:
            s_union_j = tuple(sorted(s + (j,)))
            s_union_i = tuple(sorted(s + (i,)))
            if s_union_j in winning_coalitions and s_union_i not in winning_coalitions:
                condition_one_met = False
                break

        # Condition 2:
        for t in S:
            t_union_j = tuple(sorted(t + (j,)))
            t_union_i = tuple(sorted(t + (i,)))
            if t_union_j not in winning_coalitions and t_union_i in winning_coalitions:
                condition_two_met = True

        # Both conditions satisfied.
        if condition_one_met and condition_two_met:
            return i

        # Prefer a player by weight if condition 1 is met, but condition 2 not.
        # Since every winning coalition with j is also a winning with i, but there is no coalition,
        # such that this coalition is winning with i but not with j, we can use the weight to indicate a more sensitive preferation.
        if prefer_by_weight and condition_one_met and not condition_two_met:
            if self.contributions[i - 1] > self.contributions[j - 1]:
                return i
            elif self.contributions[j - 1] > self.contributions[i - 1]:
                return j
            return None

        # Neither of the conditions satisfied, so player j is actually preferred.
        if not condition_one_met and not condition_two_met:
            return j

        # No preference.
        return None

    def get_player_ranking(self) -> Dict[Tuple, Optional[int]]:
        """Returns a ranking on the players in the game."""
        return {(i, j): self.preferred_player(i, j) for i in self.players for j in self.players[i:]}

    def get_pivot_players(self, all_coalitions=False) -> Dict[Tuple, List]:
        """
        Returns a list with all critical players with respect to every winning coalition.
        A player p is considered as pivot player in a winning coalition C if C becomes a losing coalition if p leaves C.
        """
        winning_coalitions = self.get_winning_coalitions()

        if all_coalitions:
            return {coalition:
                        [player for player in coalition if (
                                    sum(self.contributions[winning_player - 1] for winning_player in coalition) -
                                    self.contributions[player - 1]) < self.quorum and coalition in winning_coalitions]
                    for coalition in self.coalitions}
        else:
            return {winning_coalition:
                        [player for player in winning_coalition if (
                                    sum(self.contributions[winning_player - 1] for winning_player in winning_coalition) -
                                    self.contributions[player - 1]) < self.quorum]
                    for winning_coalition in winning_coalitions}
