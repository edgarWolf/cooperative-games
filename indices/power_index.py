from abc import ABC, abstractmethod
from typing import List

from games.weighted_voting_game import WeightedVotingGame
class PowerIndex(ABC):
    @abstractmethod
    def compute(self, game: WeightedVotingGame) -> List[float]:
        return

    