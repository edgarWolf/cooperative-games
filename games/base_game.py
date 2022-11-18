from abc import ABC, abstractmethod
from itertools import chain, combinations
from typing import List, Dict, Tuple


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
