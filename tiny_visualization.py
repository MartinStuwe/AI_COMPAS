import time
import sys

import pygame.display
from pygame import VIDEORESIZE

from config import level_size_x, level_size_y, scaling  # observation_space_size_x, observation_space_size_y
from helper_functions import get_obstacles_lists, get_player_positions
from level_setup import *


# how many frames per second
FPS = 60

# pygame general setup
pygame.init()
# screen = pygame.display.set_mode((observation_space_size_x*scaling, observation_space_size_y*scaling))
screen = pygame.display.set_mode((level_size_x, level_size_y))
clock = pygame.time.Clock()


def run_tiny_visualization(surface=screen, obstacles_lists_file='obstacles_list.txt', trial=237):
    obstacles_list, flag_multiple_obstacle_lists = get_obstacles_lists(obstacles_lists_file, trial)
    player_positions_filename = str(trial) + '.csv'
    player_starting_position, player_positions = get_player_positions(player_positions_filename)
    player_positions = iter(player_positions)
    level = Level(obstacles_list=obstacles_list, player_starting_position=player_starting_position, screen=surface)
    run_pygame(surface, player_positions, level)


def run_pygame(surface, player_positions, level):
    # while True:
    for player_position in player_positions:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # FIX ME: resizing not working
            if event.type == VIDEORESIZE:
                surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # update time
        # time_played = time.time() - start_time
        surface.fill('black')

        # update player position
        current_player_position = player_position
        level.run(current_player_position)

        pygame.display.update()
        clock.tick(FPS)


# time onset
start_time = time.time()
time_played = 0

run_tiny_visualization(screen, obstacles_lists_file='obstacles_list.txt', trial=237)
