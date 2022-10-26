from abc import ABC, abstractmethod
from games.game import Game

class PowerValue(ABC):
    @abstractmethod
    def compute(self, game: Game) -> list[float]:
        pass