import pygame.display
from main import run_visualization
from config import observation_space_size_x, observation_space_size_y, scaling, edge


# how many frames per second
FPS = 30

# pygame general setup
pygame.init()
screen = pygame.display.set_mode(((observation_space_size_x+(2*edge))*scaling, observation_space_size_y*scaling))

run_visualization(surface=screen, scaling=scaling, tiny_visualization=False, FPS=FPS, keyboard_input=False, 
                  obstacles_lists_file='obstacles_list.txt', drift_ranges_file="list_of_drift_ranges.txt", trial=0)
