from abc import ABC, abstractmethod
from typing import List
from coalitions.coalition import Coalition

class BaseGame(ABC):
    def __init__(self, coalitions: List[Coalition]) -> None:
        self.coaltions = coalitions

    def coalitions_summary(self):
        for coalition in self.coaltions:
            print(coalition)

    