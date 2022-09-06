import time
import sys

import pygame.display
from pygame import VIDEORESIZE

from config import level_size_y
from helper_functions import *
from level_setup import *


def run_visualization(surface, scaling=1, tiny_visualization=False, FPS=30, keyboard_input=False,
                      wall_list_file='walls_dict.txt', obstacles_lists_file='obstacles_list.txt', trial=237):
    """
    :param surface: argument for specifying pygame.display object
    :param scaling: int (or float) to scale up on-screen visualization
    :param tiny_visualization: bool argument to visualize complete level in tiny
    :param keyboard_input: bool argument needed to specify whether vis for human experiment or simple data visualization
    :param wall_list_file: file for walls_dict. Has to be in logs repository
    :param obstacles_lists_file: file for list of obstacles. Has to be in logs repository
    :param trial: player movements of which trial (.csv file in logs) to be visualized
    """
    # preparing lists of in-game objects from which to draw said objects on screen
    wall_list = get_wall_positions(wall_list_file)
    wall_list = adjust_wall_list(wall_list, scaling)
    obstacles_list, flag_multiple_obstacle_lists = get_obstacles_lists(obstacles_lists_file, trial)
    obstacles_list = adjust_obstacles_list(obstacles_list, scaling)
    player_positions_filename = str(trial) + '.csv'
    player_starting_position, player_positions = get_player_positions(player_positions_filename)
    player_starting_position, player_positions = adjust_player_positions(player_starting_position, player_positions,
                                                                         scaling, tiny_visualization=tiny_visualization)

    if not keyboard_input:
        player_positions = iter(player_positions)

    # setting up level
    level = Level(wall_list=wall_list, obstacles_list=obstacles_list, player_starting_position=player_starting_position, 
                  screen=surface, scaling=scaling)

    # running through game loop
    run_pygame(surface=surface, scaling=scaling, FPS=FPS, keyboard_input=keyboard_input,
               player_positions=player_positions, level=level, tiny_visualization=tiny_visualization)


def run_pygame(surface, scaling, FPS, keyboard_input, player_positions, level, tiny_visualization):

    clock = pygame.time.Clock()

    # time onset
    start_time = time.time()
    time_played = 0

    if keyboard_input:
        for step in range(level_size_y):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # FIX ME: resizing not working
                if event.type == VIDEORESIZE:
                    surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # update time
            time_played = time.time() - start_time
            # print(time_played)

            surface.fill('black')

            # update player position
            current_player_position = player_positions[0]
            level.run(current_player_position, scaling, tiny_visualization=tiny_visualization, keyboard_input=keyboard_input)

            pygame.display.update()
            clock.tick(FPS)
    else:
        for player_position in player_positions:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # FIX ME: resizing not working
                if event.type == VIDEORESIZE:
                    surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # update time
            time_played = time.time() - start_time
            # print(time_played)

            surface.fill('black')

            # update player position
            current_player_position = player_position
            level.run(current_player_position, scaling, tiny_visualization=tiny_visualization, keyboard_input=keyboard_input)

            pygame.display.update()
            clock.tick(FPS)
