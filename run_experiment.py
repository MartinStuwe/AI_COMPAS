import pygame.display
import time
import random
from main import run_visualization
from config import observation_space_size_x, observation_space_size_y, scaling, edge

# initialize pygame
# how many frames per second
FPS = 30

# pygame general setup
pygame.init()
screen = pygame.display.set_mode(((observation_space_size_x+(2*edge))*scaling, observation_space_size_y*scaling))

# initialize experimental procedure
trials = list(range(1, 7))  # end = 7 due to python stopping before processing 7
random.shuffle(trials)  # random shuffling of trials

# attempts_dict for monitoring attempts per trial
attempt_dict = dict.fromkeys(trials, 0)  # every trial at 0 attempts
max_attempts = 3  # maximum number of attempts given to solve trial

# run_visualization(surface=screen, scaling=scaling, tiny_visualization=False, FPS=FPS, keyboard_input=True, obstacles_lists_file='obstacles_list.txt', drift_ranges_file="list_of_drift_ranges.txt", trial=0)
