import pygame.display
import time
import random
import os
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
# random.shuffle(trials)  # random shuffling of trials

# attempts_dict for monitoring attempts per trial
attempt_dict = dict.fromkeys(trials, 0)  # every trial at 0 attempts
max_attempts = 3  # maximum number of attempts given to solve trial

# dict_keys = list(attempt_dict.keys())

title_font = pygame.font.SysFont('comicsans', 70)
background_ = pygame.image.load(os.path.join('assets/background', 'background-black.png'))
background_ = pygame.transform.scale(background_, (observation_space_size_x*scaling + 2*edge*scaling, observation_space_size_y*scaling))

quit = False
while not quit:
    level_done = False
    n_run = 0

    screen.blit(background_, (0, 0))
    title_label = title_font.render('Press SPACEBAR to start', 1, (255, 255, 255))
    screen.blit(title_label, ((observation_space_size_x*scaling + 2*edge*scaling) / 2 - title_label.get_width()/2,
                              observation_space_size_y*scaling / 2))
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                random.shuffle(trials)
                trial = trials[0]

                level_done = run_visualization(surface=screen, scaling=scaling, tiny_visualization=False, FPS=FPS,
                                               keyboard_input=True,
                                               obstacles_lists_file=f'obstacles_list_{trial}.csv',
                                               drift_ranges_file=f'drift_ranges_{trial}.csv',
                                               trial=trial, n_run=n_run)
                n_run += 1

                if level_done:
                    trials.remove(trial)
                else:
                    attempt_dict[trial] += 1
                    if attempt_dict[trial] >= 3:
                        trials.remove(trial)

                if len(trials) < 1:
                    quit = True

# print(attempt_dict)
pygame.quit()
