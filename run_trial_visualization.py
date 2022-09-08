import pygame.display
import time
from main import run_visualization
from config import observation_space_size_x, observation_space_size_y, scaling


# how many frames per second
FPS = 30

# pygame general setup
pygame.init()
screen = pygame.display.set_mode(((observation_space_size_x+(2*edge))*scaling, observation_space_size_y*scaling))

run_visualization(surface=screen, scaling=scaling, tiny_visualization=False, FPS=FPS, keyboard_input=False, 
                  wall_list_file='walls_dict.txt', obstacles_lists_file='obstacles_list.txt', trial=237)
