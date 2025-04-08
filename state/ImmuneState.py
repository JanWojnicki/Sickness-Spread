# state/ImmuneState.py
from .PersonState import PersonState

class ImmuneState(PersonState):
    def move(self, person, delta_time):
        person.default_move(delta_time)

    def update_state(self, person, delta_time):
        pass  # Osobnik odporny nie zmienia stanu

    def interact(self, person, other_person, delta_time):
        pass  # Osobnik odporny nie ulega zakażeniu ani nie zaraża
