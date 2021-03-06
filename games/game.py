from typing import List, Tuple, Dict
from games.base_game import BaseGame
import math

class Game(BaseGame):
    """Represents a class for cooperative games."""

    def __init__(self, num_players: int, contributions: List[int]) -> None:
        """Creates a new instance of this class."""
        super().__init__(num_players)
        if len(contributions) != len(self.coalitions):
            raise ValueError("Vector of contributions does not match length of coalition vector.")

        if any(contribution for contribution in contributions if contribution < 1):
            raise ValueError("Contributions have to be greater than or equal to 1.")

        # TODO : Check wether contributions grow when coalition size grows.
        self.contributions = contributions


    def characteristic_function(self) -> Dict:
        """Returns the characteristic of this TU game."""
        return { coalition : self.contributions[i] for i, coalition in enumerate(self.coalitions) }

    def get_marginal_contribution(self, coalition: Tuple, player: int) -> int:
        """Returns the marginal_contribution for a player in a coalition."""
        
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








