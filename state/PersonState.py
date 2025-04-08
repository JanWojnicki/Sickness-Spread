# state/PersonState.py
from abc import ABC, abstractmethod

#Klasa abstrakcyjna dla person state w symulacji
class PersonState(ABC):
    @abstractmethod
    def move(self, person, delta_time):
        pass

    @abstractmethod
    def update_state(self, person, delta_time):
        pass

    @abstractmethod
    def interact(self, person, other_person, delta_time):
        pass
