# state/HealthyState.py
from .PersonState import PersonState
import random
from constants import INFECTED_STATE

class HealthyState(PersonState):
    def move(self, person, delta_time):
        person.default_move(delta_time)

    def update_state(self, person, delta_time):
        pass  # Healthy person doesn't change state on their own

    def interact(self, person, other_person, delta_time):
        # Check if the other person is infected
        if other_person.state.__class__.__name__ != "InfectedState":
            return

        # Calculate distance to other person
        distance = person.position.distance_to(other_person.position)
        other_id = other_person.id

        # Distance less than 2m
        if distance <= 2.0:
            # Initialize or increment time spent close to infected person
            if other_id not in person.time_close_to_others:
                person.time_close_to_others[other_id] = 0.0
                
            person.time_close_to_others[other_id] += delta_time
            
            # Check for infection after 3 seconds of exposure
            exposure_time = 3.0
            
            # Social distancing reduces chance of infection
            if person.social_distancing:
                exposure_time += 2.0  # Need 5 seconds of exposure for people practicing distancing
            
            if person.time_close_to_others[other_id] >= exposure_time:
                # Probability calculation - symptoms increase infection chance
                base_probability = 0.5 if not other_person.has_symptoms else 0.8
                
                # Adjust probability based on distance
                distance_factor = 1.0 - (distance / 2.0) * 0.5  # 1.0 at 0m, 0.5 at 2m
                
                # Social distancing reduces infection probability
                if person.social_distancing:
                    distance_factor *= 0.7
                    
                final_probability = base_probability * distance_factor
                
                # Check for infection
                if random.random() < final_probability:
                    person.change_state(INFECTED_STATE)
                    person.time_close_to_others[other_id] = 0.0
        else:
            # Reset time if no longer close
            if other_id in person.time_close_to_others:
                person.time_close_to_others[other_id] = 0.0