# person.py
import random
import math
from models.Vector2D import Vector2D
from state.HealthyState import HealthyState
from state.InfectedState import InfectedState
from state.ImmuneState import ImmuneState
from constants import HEALTHY_STATE, INFECTED_STATE, IMMUNE_STATE

class Person:
    MAX_SPEED = 2.5  # Maximum speed
    next_id = 0  # Class variable for unique IDs

    def __init__(self, position, initial_state=HEALTHY_STATE, velocity_direction=None):
        """
        Initialize a person with position and initial state.
        
        Args:
            position (Vector2D): The initial position
            initial_state (str): Initial health state
            velocity_direction (Vector2D): Optional direction for initial velocity
        """
        self.id = Person.next_id
        Person.next_id += 1
        self.position = position  # Vector2D position
        
        # Set velocity based on direction or random
        if velocity_direction:
            speed = random.uniform(0.5, self.MAX_SPEED)
            magnitude = math.sqrt(velocity_direction.x**2 + velocity_direction.y**2)
            if magnitude > 0:
                # Normalize and scale by speed
                self.velocity = Vector2D(
                    velocity_direction.x / magnitude * speed,
                    velocity_direction.y / magnitude * speed
                )
            else:
                self.velocity = self.random_velocity()
        else:
            self.velocity = self.random_velocity()
            
        self.time_close_to_others = {}  # Time spent close to other people (keys are IDs)
        self.states = {
            HEALTHY_STATE: HealthyState(),
            INFECTED_STATE: InfectedState(),
            IMMUNE_STATE: ImmuneState()
        }
        self.state = self.states[initial_state]  # Current state
        self.infection_time = 0.0  # Time since infection
        self.infection_duration = 0.0  # Duration of infection
        self.has_symptoms = False  # Whether the person has symptoms (only applies to infected state)
        self.social_distancing = random.random() < 0.3  # 30% chance a person follows social distancing
        self.movement_timer = 0.0  # Timer for changing direction

    def random_velocity(self):
        """Generate a random velocity vector"""
        angle = random.uniform(0, 360)
        speed = random.uniform(0.5, self.MAX_SPEED)
        rad = math.radians(angle)
        return Vector2D(speed * math.cos(rad), speed * math.sin(rad))

    def default_move(self, delta_time):
        """Default movement behavior for a person"""
        # Update position
        displacement = Vector2D(self.velocity.x * delta_time, self.velocity.y * delta_time)
        self.position = Vector2D(self.position.x + displacement.x, self.position.y + displacement.y)

        # Random velocity changes
        self.movement_timer += delta_time
        change_direction_threshold = 0.1 if self.social_distancing else 0.05
        
        if self.movement_timer >= 1.0 and random.random() < change_direction_threshold:
            self.movement_timer = 0.0
            self.velocity = self.random_velocity()
            
            # Social distancing behavior: try to move away from others
            if self.social_distancing and hasattr(self, 'simulation'):
                nearby_people = [p for p in self.simulation.persons 
                                if p.id != self.id and p.position.distance_to(self.position) < 10.0]
                if nearby_people:
                    # Calculate average direction away from others
                    avg_dir_x, avg_dir_y = 0, 0
                    for other in nearby_people:
                        dir_x = self.position.x - other.position.x
                        dir_y = self.position.y - other.position.y
                        dist = math.sqrt(dir_x**2 + dir_y**2)
                        if dist > 0:  # Avoid division by zero
                            avg_dir_x += dir_x / dist
                            avg_dir_y += dir_y / dist
                    
                    if len(nearby_people) > 0:
                        avg_dir_x /= len(nearby_people)
                        avg_dir_y /= len(nearby_people)
                        
                        # Set velocity in the direction away from others
                        speed = random.uniform(0.5, self.MAX_SPEED)
                        magnitude = math.sqrt(avg_dir_x**2 + avg_dir_y**2)
                        if magnitude > 0:
                            self.velocity = Vector2D(
                                avg_dir_x / magnitude * speed,
                                avg_dir_y / magnitude * speed
                            )

    def move(self, delta_time):
        """Move according to current state"""
        self.state.move(self, delta_time)

    def update_state(self, delta_time):
        """Update state according to current state logic"""
        self.state.update_state(self, delta_time)

    def interact(self, other_person, delta_time):
        """Interact with another person"""
        self.state.interact(self, other_person, delta_time)
    
    def change_state(self, new_state):
        """Change the state of the person and initialize state attributes"""
        if new_state == INFECTED_STATE:
            self.state = self.states[INFECTED_STATE]
            self.infection_time = 0.0
            self.infection_duration = random.uniform(20.0, 30.0)  # 20-30 seconds infection
            self.has_symptoms = random.random() < 0.7  # 70% chance of symptoms
        else:
            self.state = self.states[new_state]
            self.has_symptoms = False  # Reset symptoms for other states

    def __getstate__(self):
        """Serialize person state"""
        state = self.__dict__.copy()
        state['state_name'] = self.state.__class__.__name__
        del state['state']
        del state['states']
        state['time_close_to_others_ids'] = state['time_close_to_others']
        del state['time_close_to_others']
        return state

    def __setstate__(self, state):
        """Deserialize person state"""
        state_name = state.pop('state_name')
        self.__dict__.update(state)
        self.states = {
            HEALTHY_STATE: HealthyState(),
            INFECTED_STATE: InfectedState(),
            IMMUNE_STATE: ImmuneState()
        }
        self.state = self.states[state_name]
        self.time_close_to_others = {}