# Infection Spread Simulation

A Python-based simulation modeling the spread of an infectious agent through a population using Pygame for visualization. Implements state patterns, vector math, and memento for saving/loading simulation states.

![Simulation Screenshot](link/to/screenshot.png) <!-- Add a screenshot or GIF! -->

## Features

*   **Agent-Based Modeling:** Simulates individual persons with distinct states (Healthy, Infected, Immune).
*   **State Pattern:** Cleanly manages person behavior based on their health state.
*   **Configurable Parameters:** Simulation settings (population size, infection rates, speed, etc.) are managed via `config.yaml`.
*   **Visualization:** Uses Pygame to render the simulation area and individuals.
*   **Interaction Model:** Infection spreads based on proximity and duration of contact. Distinguishes between symptomatic and asymptomatic carriers.
*   **Save/Load State:** Pause, save the current simulation state, and load previous states using the Memento pattern (press 'S' to save, 'L' to load).
*   **Boundary Handling:** Configurable behavior when agents reach the simulation boundaries (bounce, remove, wrap-around).

## Requirements

*   Python 3.8+
*   Pygame
*   PyYAML

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/infection-simulation.git
    cd infection-simulation
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the simulation from the root directory:

```bash
python main.py
