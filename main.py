import pygame
import sys
from simulation import Simulation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
from pygame import gfxdraw

# Define a modern color palette
COLORS = {
    'bg_main': (245, 246, 250),
    'panel_bg': (255, 255, 255),
    'panel_border': (230, 230, 230),
    'text_primary': (60, 60, 70),
    'text_secondary': (130, 130, 150),
    'accent': (66, 139, 202),
    'healthy': (75, 192, 112),
    'infected': (255, 76, 76),
    'infected_asymptomatic': (255, 165, 0),
    'immune': (79, 129, 255),
    'chart_bg': (250, 250, 252),
    'grid': (240, 240, 245),
    'help_overlay': (0, 0, 30, 200),
    'shadow': (0, 0, 0, 20),
}

def draw_rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
    """Draw a rectangle with rounded corners"""
    x, y, width, height = rect
    
    # Draw the main rectangle
    if border > 0 and border_color:
        pygame.draw.rect(
            surface, border_color, 
            (x-border, y-border, width+border*2, height+border*2), 
            border_radius=radius+border
        )
    
    pygame.draw.rect(
        surface, color, 
        (x, y, width, height), 
        border_radius=radius
    )

def main():
    # Window setup
    pygame.init()
    window_width, window_height = 1000, 700
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Disease Spread Simulation")
    clock = pygame.time.Clock()

    # Simulation area is smaller than the window
    sim_area_width, sim_area_height = 50, 50
    display_area_width, display_area_height = 500, 500  # Size for displaying the simulation
    sim_x_offset = 20
    sim_y_offset = 100
    
    # UI areas
    sidebar_x = display_area_width + sim_x_offset + 20
    scale_x = display_area_width / sim_area_width
    scale_y = display_area_height / sim_area_height
    
    # Statistics tracking
    history = {'healthy': [], 'infected': [], 'immune': [], 'time': []}
    chart_surface = None
    chart_update_interval = 1.0  # Update chart every second
    time_since_chart_update = 0.0
    
    # Simulation parameters
    initial_population = 100
    immune_rate = 0.1
    initial_infected = 5
    simulation = Simulation(sim_area_width, sim_area_height, initial_population, 
                           immune_rate=immune_rate, initial_infected=initial_infected)
    
    saved_states = []
    running = True
    paused = False
    show_help = False
    
    # Font setup - use more modern fonts if available
    pygame.font.init()
    try:
        title_font = pygame.font.SysFont("Segoe UI", 36, bold=True)
        main_font = pygame.font.SysFont("Segoe UI", 24)
        small_font = pygame.font.SysFont("Segoe UI", 18)
    except:
        # Fallback fonts
        title_font = pygame.font.SysFont(None, 36)
        main_font = pygame.font.SysFont(None, 24)
        small_font = pygame.font.SysFont(None, 18)
    
    def update_chart():
        nonlocal chart_surface
        # Create a figure with a modern style
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(4, 3), dpi=80)
        fig.patch.set_facecolor(tuple(c/255 for c in COLORS['chart_bg']))
        ax.set_facecolor(tuple(c/255 for c in COLORS['chart_bg']))
        
        times = history['time']
        ax.plot(times, history['healthy'], '-', color=tuple(c/255 for c in COLORS['healthy']), linewidth=3, label='Healthy')
        ax.plot(times, history['infected'], '-', color=tuple(c/255 for c in COLORS['infected']), linewidth=3, label='Infected')
        ax.plot(times, history['immune'], '-', color=tuple(c/255 for c in COLORS['immune']), linewidth=3, label='Immune')
        
        ax.set_title('Population Statistics', fontweight='bold', color=tuple(c/255 for c in COLORS['text_primary']))
        ax.set_xlabel('Time (s)', color=tuple(c/255 for c in COLORS['text_secondary']))
        ax.set_ylabel('Count', color=tuple(c/255 for c in COLORS['text_secondary']))
        ax.tick_params(colors=tuple(c/255 for c in COLORS['text_secondary']))
        
        # Modern legend
        legend = ax.legend(loc='upper right', framealpha=0.8)
        frame = legend.get_frame()
        frame.set_facecolor('white')
        frame.set_edgecolor(tuple(c/255 for c in COLORS['panel_border']))
        
        ax.grid(True, linestyle='--', alpha=0.7, color=tuple(c/255 for c in COLORS['grid']))
        
        # Convert matplotlib figure to pygame surface
        canvas = FigureCanvasAgg(fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        buffer = renderer.buffer_rgba()
        raw_data = bytes(buffer)
        size = canvas.get_width_height()
        chart_surface = pygame.image.fromstring(raw_data, size, "RGBA")
        plt.close(fig)
    
    while running:
        delta_time = clock.tick(simulation.frame_rate) / 1000.0
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_s and not paused:
                    memento = simulation.save_state()
                    saved_states.append(memento)
                    print("Simulation state saved.")
                elif event.key == pygame.K_l and not paused:
                    if saved_states:
                        memento = saved_states.pop()
                        simulation.restore_state(memento)
                        print("Simulation state loaded.")
                elif event.key == pygame.K_h:
                    show_help = not show_help
                elif event.key == pygame.K_r:
                    # Reset simulation
                    simulation = Simulation(sim_area_width, sim_area_height, initial_population, 
                                          immune_rate=immune_rate, initial_infected=initial_infected)
                    history = {'healthy': [], 'infected': [], 'immune': [], 'time': []}
                    chart_surface = None
        
        # Update simulation if not paused
        if not paused:
            simulation.update()
            simulation.time += delta_time
            time_since_chart_update += delta_time
            
            # Update statistics periodically
            if time_since_chart_update >= chart_update_interval:
                healthy_count = sum(1 for p in simulation.persons if p.state.__class__.__name__ == 'HealthyState')
                infected_count = sum(1 for p in simulation.persons if p.state.__class__.__name__ == 'InfectedState')
                immune_count = sum(1 for p in simulation.persons if p.state.__class__.__name__ == 'ImmuneState')
                
                history['healthy'].append(healthy_count)
                history['infected'].append(infected_count)
                history['immune'].append(immune_count)
                history['time'].append(simulation.time)
                
                update_chart()
                time_since_chart_update = 0
                
        # Clear screen with main background color
        screen.fill(COLORS['bg_main'])
        
        # Draw simulation panel with shadow and border
        panel_rect = (sim_x_offset-10, sim_y_offset-10, display_area_width+20, display_area_height+20)
        shadow_rect = (panel_rect[0]+5, panel_rect[1]+5, panel_rect[2], panel_rect[3])
        
        # Draw shadow first (subtle effect)
        shadow_surface = pygame.Surface((panel_rect[2], panel_rect[3]), pygame.SRCALPHA)
        shadow_surface.fill(COLORS['shadow'])
        screen.blit(shadow_surface, (shadow_rect[0], shadow_rect[1]))
        
        # Draw main simulation panel
        draw_rounded_rect(
            screen, 
            COLORS['panel_bg'], 
            panel_rect, 
            radius=15, 
            border=2, 
            border_color=COLORS['panel_border']
        )
        
        # Draw simulation area
        draw_rounded_rect(
            screen, 
            (255, 255, 255), 
            (sim_x_offset, sim_y_offset, display_area_width, display_area_height), 
            radius=10
        )
        
        # Draw title with subtle shadow for depth
        title = title_font.render("Disease Spread Simulation", True, COLORS['text_primary'])
        screen.blit(title, (window_width // 2 - title.get_width() // 2, 20))
        
        # Draw persons with improved visualization
        for person in simulation.persons:
            # Convert simulation coordinates to screen coordinates with proper scaling
            x = int(person.position.x * scale_x) + sim_x_offset
            y = int(person.position.y * scale_y) + sim_y_offset
            
            state_name = person.state.__class__.__name__
            radius = 5
            
            if state_name == 'InfectedState':
                color = COLORS['infected'] if person.has_symptoms else COLORS['infected_asymptomatic']
                
                # Draw glow around infected
                max_radius = 10 if person.has_symptoms else 8
                for r in range(max_radius, radius, -1):
                    alpha = 50 - (max_radius - r) * 10
                    if alpha > 0:
                        glow_color = (*color[:3], alpha)
                        gfxdraw.filled_circle(screen, x, y, r, glow_color)
                
            elif state_name == 'ImmuneState':
                color = COLORS['immune']
            else:  # HealthyState
                color = COLORS['healthy']
            
            # Draw anti-aliased circle for smoother look
            gfxdraw.aacircle(screen, x, y, radius, color)
            gfxdraw.filled_circle(screen, x, y, radius, color)
        
        # Draw statistics panel with modern styling
        stats_panel_rect = (sidebar_x, sim_y_offset, window_width - sidebar_x - 20, 200)
        draw_rounded_rect(
            screen, 
            COLORS['panel_bg'], 
            stats_panel_rect, 
            radius=15, 
            border=0
        )
        
        # Add a subtle header to the stats panel
        header_rect = (stats_panel_rect[0], stats_panel_rect[1], stats_panel_rect[2], 40)
        draw_rounded_rect(
            screen, 
            COLORS['accent'], 
            header_rect, 
            radius=15
        )
        # Cut the bottom corners
        pygame.draw.rect(
            screen,
            COLORS['accent'],
            (header_rect[0], header_rect[1] + header_rect[3] - 15, header_rect[2], 15)
        )
        
        stats_title = main_font.render("Statistics", True, (255, 255, 255))
        screen.blit(stats_title, (sidebar_x + 20, sim_y_offset + 10))
        
        healthy_count = sum(1 for p in simulation.persons if p.state.__class__.__name__ == 'HealthyState')
        infected_count = sum(1 for p in simulation.persons if p.state.__class__.__name__ == 'InfectedState')
        immune_count = sum(1 for p in simulation.persons if p.state.__class__.__name__ == 'ImmuneState')
        total = len(simulation.persons)
        
        stats_text = [
            f"Total Population: {total}",
            f"Healthy: {healthy_count} ({healthy_count/total*100:.1f}%)" if total > 0 else "Healthy: 0 (0.0%)",
            f"Infected: {infected_count} ({infected_count/total*100:.1f}%)" if total > 0 else "Infected: 0 (0.0%)",
            f"Immune: {immune_count} ({immune_count/total*100:.1f}%)" if total > 0 else "Immune: 0 (0.0%)",
            f"Time: {simulation.time:.1f}s",
        ]
        
        # Statistics text display
        for i, text in enumerate(stats_text):
            text_surface = main_font.render(text, True, COLORS['text_primary'])
            screen.blit(text_surface, (sidebar_x + 20, sim_y_offset + 50 + i * 25))
        
        # Status indicator moved to top right corner
        status_color = COLORS['healthy'] if not paused else COLORS['infected_asymptomatic']
        status_text = "▶ Running" if not paused else "❚❚ Paused"
        status_surface = main_font.render(status_text, True, status_color)
        
        # Create a status panel in the top right corner
        status_panel_width = 150
        status_panel_height = 36
        status_panel_rect = (window_width - status_panel_width - 20, 20, status_panel_width, status_panel_height)
        draw_rounded_rect(
            screen,
            (240, 240, 245),  # Light background for status
            status_panel_rect,
            radius=10
        )
        
        # Center the status text in the panel
        status_x = status_panel_rect[0] + (status_panel_rect[2] - status_surface.get_width()) // 2
        status_y = status_panel_rect[1] + (status_panel_rect[3] - status_surface.get_height()) // 2
        screen.blit(status_surface, (status_x, status_y))
        
        # Draw chart in a nice panel if available
        if chart_surface:
            chart_panel_rect = (sidebar_x, sim_y_offset + 220, chart_surface.get_width() + 20, chart_surface.get_height() + 20)
            draw_rounded_rect(
                screen, 
                COLORS['panel_bg'], 
                chart_panel_rect, 
                radius=15, 
                border=0
            )
            screen.blit(chart_surface, (sidebar_x + 10, sim_y_offset + 230))
        
        # Draw controls help
        if show_help:
            help_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
            help_surface.fill(COLORS['help_overlay'])
            screen.blit(help_surface, (0, 0))
            
            help_text = [
                "Controls:",
                "P - Pause/Resume simulation",
                "S - Save current state",
                "L - Load last saved state",
                "R - Reset simulation",
                "H - Toggle this help screen",
                "",
                "Click anywhere to close"
            ]
            
            for i, text in enumerate(help_text):
                help_line = main_font.render(text, True, (255, 255, 255))
                screen.blit(help_line, (window_width//2 - help_line.get_width()//2, window_height//3 + i*30))
                
            if pygame.mouse.get_pressed()[0]:
                show_help = False
        else:
            # Enhanced help hint
            hint = small_font.render("Press H for help", True, COLORS['text_secondary'])
            hint_rect = hint.get_rect(bottomright=(window_width - 10, window_height - 10))
            screen.blit(hint, hint_rect)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
