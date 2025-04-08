# simulation_memento.py
import copy
import datetime

class SimulationMemento:
    def __init__(self, simulation):
        """
        Create a deep copy of the simulation state
        
        Args:
            simulation: The simulation object to save
        """
        self.state = {
            'persons': copy.deepcopy(simulation.persons),
            'time': simulation.time
        }
        self.timestamp = datetime.datetime.now()
        self.statistics = {
            'total': len(simulation.persons),
            'healthy': sum(1 for p in simulation.persons if p.state.__class__.__name__ == 'HealthyState'),
            'infected': sum(1 for p in simulation.persons if p.state.__class__.__name__ == 'InfectedState'),
            'immune': sum(1 for p in simulation.persons if p.state.__class__.__name__ == 'ImmuneState')
        }
    
    def get_summary(self):
        """Return a summary of this saved state"""
        return {
            'timestamp': self.timestamp,
            'simulation_time': self.state['time'],
            'statistics': self.statistics
        }
