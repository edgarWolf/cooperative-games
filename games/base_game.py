from abc import ABC, abstractmethod
from typing import List
from itertools import chain, combinations
from coalitions.coalition import Coalition

class BaseGame(ABC):
    def __init__(self, players: List[int]) -> None:
        self.players = players
        self.coaltions = self.__init_coalitions(players)


    def player_summary(self):
        for player in self.players:
            print(player)

    def __init_coalitions(self, players: List[int]) -> List[Coalition]:
        powerset = self.__powerset(players)
        return powerset
        

    def __powerset(self, elements: List) -> List:
        s = list(elements)
        return list(chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1)))

    