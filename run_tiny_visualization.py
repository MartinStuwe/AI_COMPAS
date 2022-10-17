import pygame.display
from main import run_visualization
from config import level_size_x, level_size_y, scaling_tiny_vis, edge


# how many frames per second
FPS = 60

# pygame general setup
pygame.init()
screen = pygame.display.set_mode(((level_size_x+(2*edge))*scaling_tiny_vis, level_size_y*scaling_tiny_vis))

run_visualization(surface=screen, scaling=scaling_tiny_vis, tiny_visualization=True, FPS=FPS, keyboard_input=False,
                  obstacles_lists_file='obstacles_list_0.csv', drift_ranges_file='drift_ranges_0.csv', trial=0)
