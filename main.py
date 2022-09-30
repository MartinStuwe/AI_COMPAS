import time
import sys

import pygame.display
from pygame import VIDEORESIZE

from config import level_size_y, pre_trial_steps, observation_space_size_x, observation_space_size_y, scaling, edge
from helper_functions import *
from level_setup import *


def run_visualization(surface, scaling=1, tiny_visualization=False, FPS=30, keyboard_input=False,
                      obstacles_lists_file='obstacles_list.txt', drift_ranges_file="list_of_drift_ranges.txt",
                      trial=4):
    """
    :param surface: argument for specifying pygame.display object
    :param scaling: int (or float) to scale up on-screen visualization
    :param tiny_visualization: bool argument to visualize complete level in tiny
    :param FPS: frames per second. 30 as default value. For smoother animation choose 60.
    :param keyboard_input: bool argument needed to specify whether vis for human experiment or simple data visualization
    :param obstacles_lists_file: file for list of obstacles. Has to be in logs repository
    :param drift_ranges_file: file for drift ranges. Has to be in logs repository
    :param trial: player movements of which trial (.csv file in logs) to be visualized
    """
    # preparing lists of in-game objects from which to draw said objects on screen
    # walls will be the same across all experimental trials
    wall_list = get_wall_positions("walls_dict.txt")
    wall_list = adjust_wall_list(wall_list, scaling)

    obstacles_list, flag_multiple_obstacle_lists = get_obstacles_lists(obstacles_lists_file, trial)
    obstacles_list = adjust_obstacles_list(obstacles_list, scaling)

    player_positions_filename = str(trial) + '_vis.csv'
    player_starting_position, player_positions = get_player_positions(player_positions_filename)
    player_starting_position, player_positions = adjust_player_positions(player_starting_position, player_positions,
                                                                             scaling, tiny_visualization=tiny_visualization)
    drift_ranges = get_drift_ranges(drift_ranges_file, level=trial)
    drift_ranges = adjust_drift_ranges(drift_ranges, scaling)

    if not keyboard_input:
        player_positions = iter(player_positions)

    # setting up level
    # level = Level(wall_list=wall_list, obstacles_list=obstacles_list,
    # player_starting_position=player_starting_position, drift_ranges=drift_ranges, screen=surface, scaling=scaling,
    # keyboard_input=keyboard_input)

    # running through game loop
    if keyboard_input:
        main_menu(wall_list=wall_list, obstacles_list=obstacles_list, player_starting_position=player_starting_position,
                  drift_ranges=drift_ranges, surface=surface, scaling=scaling, FPS=FPS, keyboard_input=keyboard_input,
                  player_positions=player_positions, tiny_visualization=tiny_visualization)

    else:
        run_pygame(surface=surface, scaling=scaling, FPS=FPS, keyboard_input=keyboard_input,
                   player_positions=player_positions, level=level, tiny_visualization=tiny_visualization)


def run_pygame(surface, scaling, FPS, keyboard_input, player_positions, level, tiny_visualization):

    clock = pygame.time.Clock()

    # time onset
    start_time = time.time()
    time_played = 0

    if keyboard_input:
        level_done = False
        while not level_done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # FIXME: resizing not working
                if event.type == VIDEORESIZE:
                    surface = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # update time
            time_played = time.time() - start_time
            # print(time_played)

            surface.fill('black')

            # update player position
            current_player_position = player_positions[0]  # not needed but still given in level.run()
            level_done = level.run(current_player_position, scaling, tiny_visualization=tiny_visualization, keyboard_input=keyboard_input)

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


def main_menu(wall_list, obstacles_list, player_starting_position, drift_ranges, surface, scaling, FPS, keyboard_input,
              player_positions, tiny_visualization):
    title_font = pygame.font.SysFont('comicsans', 70)
    background_ = pygame.image.load(os.path.join('assets/background', 'background-black.png'))
    background_ = pygame.transform.scale(background_, (observation_space_size_x*scaling + 2*edge*scaling,
                                                       observation_space_size_y*scaling))
    level_done = False
    while not level_done:
        surface.blit(background_, (0, 0))
        title_label = title_font.render('Press any key to start', 1, (255, 255, 255))
        surface.blit(title_label, ((observation_space_size_x*scaling + 2*edge*scaling) / 2 - title_label.get_width()/2,
                     observation_space_size_y*scaling / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                level_done = True
            if event.type == pygame.KEYDOWN:
                level = Level(wall_list=wall_list, obstacles_list=obstacles_list,
                              player_starting_position=player_starting_position,
                              drift_ranges=drift_ranges, screen=surface, scaling=scaling, keyboard_input=keyboard_input)

                run_pygame(surface=surface, scaling=scaling, FPS=FPS, keyboard_input=keyboard_input,
                           player_positions=player_positions, level=level, tiny_visualization=tiny_visualization)
    pygame.quit()
