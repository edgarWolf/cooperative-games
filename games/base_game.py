from abc import ABC, abstractmethod
from typing import List, Tuple, Dict
from itertools import chain, combinations

class BaseGame(ABC):
    """
    Represents a base class for games in context of game theory.
    """
    def __init__(self, num_players) -> None:
        """Base constructor for all derived classes."""
        self._players = [i for i in range(1, num_players + 1)]
        self._coalitions = self.__init_coalitions()


    @property
    def players(self) -> List[int]:
        """Property for players field."""
        return self._players

    @property
    def coalitions(self) -> Dict:
        """Property for coalitions field."""
        return self._coalitions

    @abstractmethod
    def characteristic_function(self) -> Dict:
        """Returns the characteristic function of the game."""
        return

    def __init_coalitions(self) -> List[Tuple]:
        """Returns all possible coalitions based on the player vector of the current game."""
        powerset = self.__powerset(self.players)
        return powerset
        

    def __powerset(self, elements: List) -> List[Tuple]:
        """Returns the powerset from a given list."""
        return list(chain.from_iterable(combinations(elements, r) for r in range(1, len(elements)+1)))



    