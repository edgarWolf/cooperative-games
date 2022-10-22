from games.base_game import BaseGame

class WeightedVotingGame(BaseGame):
    """
    Represents the class of weighted voting games. Each coalition with a sum of weights greater than or equal to the quorum are considered winning coalitions, losing otherwise.
    """
    def __init__(self, num_players: int, weights: list[int], quorum : int) -> None:
        """Creates a new instance of this class."""
        super().__init__(num_players)

        # Parameter check.
        if len(weights) != num_players:
            raise ValueError("Length of player vector and weight vector don't match.")
        if any(weight  for weight  in weights  if weight  < 0):
            raise ValueError("Weight vector containns nonallowed negative weights.")
        if quorum < 0:
            raise ValueError("Qurom is only allowed to be greater than 0.")

        self.weigths = weights
        self.quorum = quorum

    def characteristic_function(self) -> dict[tuple, int]:
        """Returns the characteristic function of this weighted voting game."""
        return { coalition :  1 if sum(self.weigths[player - 1] for player in coalition) >= self.quorum else 0 for coalition in self.coalitions }

    def get_minimal_winning_coalitions(self) -> list[tuple]:
        """Returns a list of the minimal winning coalitions."""
        critical_coalitions = self.get_pivot_players()
        return [coalition for coalition, critical_players in critical_coalitions.items() if coalition == tuple(critical_players)]


    def get_winning_coalitions(self) -> list[tuple]:
        """Returns a list containing winning coalitions, i.e all coalitions with a sum of weights >= the quorum."""
        return [coalition for coalition in self.coalitions if sum(self.weigths[player - 1] for player in coalition) >= self.quorum]

    def get_shift_winning_coalitions(self) -> list[tuple]:
        """
        Returns a list containing all shift-minimal coalitions. 
        A minimal winning coalition S in W_m is called shift-minimal, if it holds, that
        for every player i in S and every player j not in S with i > j, it holds:
            (S/{i}) union {j} not in W_m.
        A shift minimal winning coalition is therefore are minimal winning coalition, where no player can not be replaced by a less desired player.
        """

        W_m = self.get_minimal_winning_coalitions()
        shift_minmimal_winning_coalitions = []
        unique_pivot_players = set(sum(W_m, ()))
        for S in W_m:
            is_condition_met = True
            for i in S:
                players_not_in_S = [player for player in unique_pivot_players if player not in S and self.preferred_player(i, player) == i] 
                
                for j in players_not_in_S:
                    S_without_i = tuple(p for p in S if p != i)
                    S_without_i_union_j = tuple(sorted( S_without_i + (j,) ))
                    # Found a minimal winning coalition by shifting with a less desirable player --> Not shift minimal.
                    if S_without_i_union_j in W_m:
                        is_condition_met = False
                        break

                # Break out of outer loop
                if not is_condition_met:
                    break
            
            if is_condition_met:
                shift_minmimal_winning_coalitions.append(S)

        return shift_minmimal_winning_coalitions

    def preferred_player(self, i: int, j: int, prefer_by_weight: bool = True) -> int:
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
            if self.weigths[i - 1] > self.weigths[j - 1]:
                return i
            elif self.weigths[j - 1] > self.weigths[i -1]:
                return j
            return None

        # Neither of the conditions satiesfied, so player j is actually preferred.
        if not condition_one_met and not condition_two_met:
            return j

        # No preference.
        return None

    def get_player_ranking(self) -> list[int]:
        """Returns a ranking on the players in the game."""
        preferations = {}
        for i in self.players:
            for j in self.players[i:]:
                preferred_player = self.preferred_player(i, j)
                preferations[(i, j)] = preferred_player
        return preferations


    def get_pivot_players(self, all_coalitions=False) -> dict[tuple, list]:
        """
        Returns a list with all critical players with respect to every winning coalition. 
        A player p is considered as pivot player in a winning coalition C if C becomes a losing coalition if p leaves C.
        """
        winning_coalitions = self.get_winning_coalitions()

        if all_coalitions:
            return { coalition : 
                                [player for player in coalition if  ( sum(self.weigths[winning_player - 1] for winning_player in coalition) - self.weigths[player - 1] ) < self.quorum and coalition in winning_coalitions ] 
                                for coalition in self.coalitions }
        else:
            return { winning_coaliton : 
                    [player for player in winning_coaliton if  ( sum(self.weigths[winning_player - 1] for winning_player in winning_coaliton) - self.weigths[player - 1] ) < self.quorum ] 
                    for winning_coaliton in winning_coalitions }
            
