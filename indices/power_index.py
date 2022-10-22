from abc import ABC, abstractmethod

from games.weighted_voting_game import WeightedVotingGame
class PowerIndex(ABC):
    @abstractmethod
    def compute(self, game: WeightedVotingGame) -> list[float]:
        return

    