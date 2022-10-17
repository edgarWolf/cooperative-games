from abc import ABC, abstractmethod
from typing import List

from games.weighted_voting_game import WeightedVotingGame
class PowerIndex(ABC):
    def __init__(self, game: WeightedVotingGame) -> None:
        self._game = game

    @property
    def game(self) -> WeightedVotingGame:
        """Property for game field."""
        return self._game
    
    @abstractmethod
    def compute(self) -> List[float]:
        return

    