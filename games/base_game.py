from abc import ABC, abstractmethod
from typing import List
from itertools import chain, combinations
from coalitions.coalition import Coalition

class BaseGame(ABC):
    """
    Represents a base class for games in context of game theory.
    """
    def __init__(self, players: List[int]) -> None:
        """Base constructor for all derived classes."""
        self._players = players
        self._coalitions = self.__init_coalitions()


    @property
    def players(self) -> List[int]:
        """Property for players field."""
        return self._players

    @property
    def coalitions(self) -> List[Coalition]:
        """Property for coalitions field."""
        return self._coalitions

    def __init_coalitions(self) -> List[Coalition]:
        """Returns all possible coalitions based on the player vector of the current game."""
        powerset = self.__powerset(self.players)
        return powerset
        

    def __powerset(self, elements: List) -> List:
        """Returns the powerset from a given list."""
        s = list(elements)
        return list(chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1)))

    