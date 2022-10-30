from abc import ABC, abstractmethod
from itertools import chain, combinations

class BaseGame(ABC):
    """
    Represents a base class for games in context of game theory.
    """
    def __init__(self, contributions: list[int]) -> None:
        """Base constructor for all derived classes."""
        if not contributions:
            raise ValueError("No contributions provided.")

        self._players = []
        self._coalitions = []
        self._contributions = []

    @property
    def players(self) -> list[int]:
        """Property for players field."""
        return self._players

    @property
    def coalitions(self) -> list[tuple]:
        """Property for coalitions field."""
        return self._coalitions

    @property
    def contributions(self) -> list[int]:
        """Property for contributions field."""
        return self._contributions

    @abstractmethod
    def characteristic_function(self) -> dict[tuple, int]:
        """Returns the characteristic function of the game."""
        return

    def _init_coalitions(self) -> list[tuple]:
        """Returns all possible coalitions based on the player vector of the current game."""
        powerset = self.__powerset(self.players)
        return powerset
        

    def __powerset(self, elements: list) -> list[tuple]:
        """Returns the powerset from a given list."""
        return list(chain.from_iterable(combinations(elements, r) for r in range(1, len(elements)+1)))

    def get_one_coalitions(self) -> list[tuple]:
        """Returns a list of one coalitions exisiting in the current game."""
        return [coalition for coalition in self.coalitions if len(coalition) == 1]



    