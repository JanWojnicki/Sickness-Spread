# simulation.py
import random
from person import Person
from models.Vector2D import Vector2D
from simulation_memento import SimulationMemento
from constants import HEALTHY_STATE, INFECTED_STATE, IMMUNE_STATE

#Środowisko symulacji
class Simulation:
    def __init__(self, area_width, area_height, initial_population, immune_rate=0.0, initial_infected=0):
        """
        Initialize the simulation environment.
        
        Args:
            area_width (float): Width of the simulation area
            area_height (float): Height of the simulation area
            initial_population (int): Initial number of people in the simulation
            immune_rate (float): Percentage of initially immune people (0.0-1.0)
            initial_infected (int): Number of initially infected people
        """
        self.area_width = area_width
        self.area_height = area_height
        self.persons = []  # List of people in the simulation
        self.persons_by_id = {}
        self.time = 0.0  # Simulation time
        self.frame_rate = 60  # Frames per second (increased for smoother animation)
        self.delta_time = 1.0 / self.frame_rate
        
        # Person spawn parameters
        self.spawn_rate = 0.05  # Base chance for a new person to appear per update
        self.max_population = 300  # Limit the population size

        # Initialize population
        for _ in range(initial_population):
            position = Vector2D(random.uniform(0, area_width), random.uniform(0, area_height))
            if random.random() < immune_rate:
                initial_state = IMMUNE_STATE
            else:
                initial_state = HEALTHY_STATE
            person = Person(position, initial_state=initial_state)
            self.persons.append(person)
            self.persons_by_id[person.id] = person

        # Randomly infect initial people
        for person in random.sample(self.persons, min(initial_infected, len(self.persons))):
            person.change_state(INFECTED_STATE)

    def run(self):
        while True:
            self.update()
            self.time += self.delta_time

    def update(self):
        """Update the simulation state for one time step"""
        # Update each person's state
        for person in self.persons[:]:  # Copy list to be able to remove people
            person.move(self.delta_time)
            person.update_state(self.delta_time)

            # Check interactions with other people
            for other_person in self.persons:
                if other_person.id == person.id:
                    continue  # Don't check interaction with self
                person.interact(other_person, self.delta_time)

            # Check area boundaries
            self.check_bounds(person)

        # Add new people occasionally if below max population
        if len(self.persons) < self.max_population and random.random() < self.spawn_rate:
            self.spawn_person()

    #Sprawdza czy osoba jest w obszarze symulacji
    def check_bounds(self, person):
        """Check if a person is within the bounds of the simulation area"""
        x, y = person.position.x, person.position.y
        left, right = 0, self.area_width
        top, bottom = 0, self.area_height

        out_of_bounds = False
        if x < left:
            out_of_bounds = True
        elif x > right:
            out_of_bounds = True
        if y < top:
            out_of_bounds = True
        elif y > bottom:
            out_of_bounds = True

        if out_of_bounds:
            if random.random() < 0.7:  # 70% chance to bounce back
                # Reflect velocity to stay in bounds
                if x < left or x > right:
                    person.velocity.x *= -1
                if y < top or y > bottom:
                    person.velocity.y *= -1
                
                # Correct position to be within bounds
                person.position.x = max(min(person.position.x, right), left)
                person.position.y = max(min(person.position.y, bottom), top)
            else:
                # Remove person from simulation (30% chance)
                self.persons.remove(person)
                del self.persons_by_id[person.id]

    def spawn_person(self):
        """Generate a new person at the border of the simulation area"""
        # Random position on the border
        side = random.choice(['left', 'right', 'top', 'bottom'])
        if side == 'left':
            position = Vector2D(0, random.uniform(0, self.area_height))
            velocity_direction = Vector2D(1, random.uniform(-0.5, 0.5))
        elif side == 'right':
            position = Vector2D(self.area_width, random.uniform(0, self.area_height))
            velocity_direction = Vector2D(-1, random.uniform(-0.5, 0.5))
        elif side == 'top':
            position = Vector2D(random.uniform(0, self.area_width), 0)
            velocity_direction = Vector2D(random.uniform(-0.5, 0.5), 1)
        else:  # bottom
            position = Vector2D(random.uniform(0, self.area_width), self.area_height)
            velocity_direction = Vector2D(random.uniform(-0.5, 0.5), -1)

        # Create new person with velocity pointing inward
        person = Person(position, velocity_direction=velocity_direction)
        
        # 10% chance of being infected when entering
        if random.random() < 0.1:
            person.change_state(INFECTED_STATE)
            
        self.persons.append(person)
        self.persons_by_id[person.id] = person

    def save_state(self):
        """Create a memento with the current simulation state"""
        return SimulationMemento(self)

    def restore_state(self, memento):
        """Restore simulation state from a memento"""
        self.persons = memento.state['persons']
        self.time = memento.state['time']
        # Reconstruct persons_by_id dictionary
        self.persons_by_id = {person.id: person for person in self.persons}
        # Reconstruct time_close_to_others for each person
        for person in self.persons:
            time_close_to_others_ids = getattr(person, 'time_close_to_others_ids', {})
            person.time_close_to_others = {}
            for other_id, time in time_close_to_others_ids.items():
                if other_id in self.persons_by_id:
                    other_person = self.persons_by_id[other_id]
                    person.time_close_to_others[other_id] = time
            if hasattr(person, 'time_close_to_others_ids'):
                del person.time_close_to_others_ids
