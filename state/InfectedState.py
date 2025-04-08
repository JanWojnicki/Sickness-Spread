# state/InfectedState.py
from .PersonState import PersonState
from constants import IMMUNE_STATE

class InfectedState(PersonState):
    def move(self, person, delta_time):
        person.default_move(delta_time)

    #Jeśli przekroczy czas infekcji to zmienia stan na immune
    def update_state(self, person, delta_time):
        person.infection_time += delta_time
        if person.infection_time >= person.infection_duration:
            person.change_state(IMMUNE_STATE)  # Użyj stałej

    def interact(self, person, other_person, delta_time):
        pass  # Zakażony osobnik nie zaraża innych bezpośrednio
