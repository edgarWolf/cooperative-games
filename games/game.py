from typing import List, Tuple, Dict
from games.base_game import BaseGame
from scipy.special import binom

class Game(BaseGame):
    """Represents a class for cooperative games."""

    def __init__(self, num_players: int, contributions: List[int]) -> None:
        """Creates a new instance of this class."""
        super().__init__(num_players)
        if len(contributions) != len(self.coalitions):
            raise ValueError("Vector of contributions does not match length of coalition vector.")

        if any(contribution for contribution in contributions if contribution < 0):
            raise ValueError("Contributions have to be greater than or equal to 0.")

        if not self.__check_if_contributions_are_monotone(contributions):
            raise ValueError("Contributions have to grow monotone by coalition size.")

        self.contributions = contributions


    def characteristic_function(self) -> Dict:
        """Returns the characteristic of this TU game."""
        return { coalition : self.contributions[i] for i, coalition in enumerate(self.coalitions) }

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
    
    def get_utopia_payoff_vector(self):
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
            v_N_without_i = v[tuple(sorted(p for p in N if p != player))] if N_without_i in v else 0
            M.append(v_N - v_N_without_i)
        return M


    def get_minimal_rights_vector(self):
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



                



   
    
    def __check_if_contributions_are_monotone(self, contributions):
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











