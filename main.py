import time
import sys

import pygame.display
from pygame import VIDEORESIZE

from config import level_size_y, pre_trial_steps, observation_space_size_x, observation_space_size_y, scaling, edge
from helper_functions import *
from level_setup import *


def run_visualization(surface, scaling=1, tiny_visualization=False, FPS=30, keyboard_input=False,
                      obstacles_lists_file='obstacles_list.csv', drift_ranges_file='drift_ranges.csv',
                      trial=0, attempt=0, n_run=0):
    """
    :param surface: argument for specifying pygame.display object
    :param scaling: int (or float) to scale up on-screen visualization
    :param tiny_visualization: bool argument to visualize complete level in tiny
    :param FPS: frames per second. 30 as default value. For smoother animation choose 60.
    :param keyboard_input: bool argument needed to specify whether vis for human experiment or simple data visualization
    :param obstacles_lists_file: file for list of obstacles. Has to be in logs repository
    :param drift_ranges_file: file for drift ranges. Has to be in logs repository
    :param trial: player movements of which trial (.csv file in logs) to be visualized
    :param attempt: attempts for this specific trial
    :param n_run: total number of runs in this specific experiment / visualization
    """
    # preparing lists of in-game objects from which to draw said objects on screen
    # walls will be the same across all experimental trials
    wall_list = get_wall_positions('walls_dict.txt')
    wall_list = adjust_wall_list(wall_list, scaling)

    obstacles_list, flag_multiple_obstacle_lists = get_obstacles_lists(obstacles_lists_file)
    obstacles_list = adjust_obstacles_list(obstacles_list, scaling)

    if keyboard_input:
        player_positions_filename = '0_vis.csv'
    else:
        player_positions_filename = str(trial) + '_vis.csv'
    player_starting_position, player_positions = get_player_positions(player_positions_filename)
    player_starting_position, player_positions = adjust_player_positions(player_starting_position, player_positions,
                                                                         scaling, tiny_visualization=tiny_visualization)

    drift_ranges = get_drift_ranges(drift_ranges_file)
    drift_ranges = adjust_drift_ranges(drift_ranges, scaling)

    if not keyboard_input:
        player_positions = iter(player_positions)

    # running through game loop
    if keyboard_input:
        level = Level(wall_list=wall_list, obstacles_list=obstacles_list,
                      player_starting_position=player_starting_position,
                      drift_ranges=drift_ranges, screen=surface, scaling=scaling, n_run=n_run,
                      keyboard_input=keyboard_input, trial=trial, attempt=attempt)

        level_done = run_pygame(surface=surface, scaling=scaling, FPS=FPS, keyboard_input=keyboard_input,
                                player_positions=player_positions, level=level, tiny_visualization=tiny_visualization)
        return level_done
    else:
        level = Level(wall_list=wall_list, obstacles_list=obstacles_list,
                      player_starting_position=player_starting_position,
                      drift_ranges=drift_ranges, screen=surface, scaling=scaling,
                      keyboard_input=keyboard_input)

        run_pygame(surface=surface, scaling=scaling, FPS=FPS, keyboard_input=keyboard_input,
                   player_positions=player_positions, level=level, tiny_visualization=tiny_visualization)


def run_pygame(surface, scaling, FPS, keyboard_input, player_positions, level, tiny_visualization):

    clock = pygame.time.Clock()

    # time onset
    start_time = time.time()
    level_done = False

    if keyboard_input:
        quit = False
        while not quit:
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
            quit, level_done = level.run(time_played, current_player_position, scaling, tiny_visualization=tiny_visualization, keyboard_input=keyboard_input)

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

            surface.fill('black')

            # update player position
            current_player_position = player_position
            level.run(time_played, current_player_position, scaling, tiny_visualization=tiny_visualization, keyboard_input=keyboard_input)

            pygame.display.update()
            clock.tick(FPS)

    return level_done


def main_menu(wall_list, obstacles_list, player_starting_position, drift_ranges, surface, scaling, FPS, keyboard_input,
              player_positions, tiny_visualization, trial, attempt):
    title_font = pygame.font.SysFont('comicsans', 70)
    background_ = pygame.image.load(os.path.join('assets/background', 'background-black.png'))
    background_ = pygame.transform.scale(background_, (observation_space_size_x*scaling + 2*edge*scaling,
                                                       observation_space_size_y*scaling))
    n_run = 0
    level_done = False
    quit = False

    while not quit:
        surface.blit(background_, (0, 0))
        title_label = title_font.render('Press SPACEBAR to start', 1, (255, 255, 255))
        surface.blit(title_label, ((observation_space_size_x*scaling + 2*edge*scaling) / 2 - title_label.get_width()/2,
                     observation_space_size_y*scaling / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    level = Level(wall_list=wall_list, obstacles_list=obstacles_list,
                                  player_starting_position=player_starting_position,
                                  drift_ranges=drift_ranges, screen=surface, scaling=scaling, n_run=n_run,
                                  keyboard_input=keyboard_input, trial=trial, attempt=attempt)

                    level_done = run_pygame(surface=surface, scaling=scaling, FPS=FPS, keyboard_input=keyboard_input, 
                                            player_positions=player_positions, level=level, tiny_visualization=tiny_visualization)
                    n_run += 1
    pygame.quit()
    return level_done
