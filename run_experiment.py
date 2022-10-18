import pygame.display
import time
import random
import os
from main import run_visualization
from config import observation_space_size_x, observation_space_size_y, scaling, edge


# participant code
code = input('Enter code: ')

# initialize pygame
# how many frames per second
FPS = 30

# pygame general setup
pygame.init()
screen = pygame.display.set_mode(((observation_space_size_x + (2 * edge)) * scaling,
                                  observation_space_size_y * scaling))

# initialize experimental procedure
N_trials = 6  # for each trial there must be a drift_ranges & obstacles_list file in the logs folder
trials = list(range(1, N_trials + 1))  # end +1 due to python stopping before processing last entry
# trials list is our loop object. We will remove trials from here when they are attempted 3 times already
# or have been solved completely

# attempts_dict for monitoring attempts per trial
attempt_dict = dict.fromkeys(trials, 0)  # every trial at 0 attempts
max_attempts = 3  # maximum number of attempts given to solve trial

# features of displayed text
WHITE = (255, 255, 255)

title_font = pygame.font.SysFont('Calibri', 70, bold=True)
text_font = pygame.font.SysFont('Calibri', 35, bold=True)


def display_instructions(surface):
    surface.fill('black')
    with open("assets/instructions/instructions_text.txt") as f:
        for n, line in enumerate(f):
            instruction_text = text_font.render(line.rstrip('\r\n'), True, WHITE)  # rstrip gets rid of trailing newline characters
            text_rect = instruction_text.get_rect()
            text_rect.centerx = (observation_space_size_x * scaling + 2 * edge * scaling) // 2
            text_rect.centery = n * 50 + 100
            surface.blit(instruction_text, text_rect)


def display_intertrial_screen(surface):
    surface.fill('black')
    title_lable = title_font.render('Press SPACEBAR to start', 1, WHITE)
    title_rect = title_lable.get_rect()
    title_rect.centerx = (observation_space_size_x * scaling + 2 * edge * scaling) // 2
    title_rect.centery = (observation_space_size_y * scaling) // 2
    surface.blit(title_lable, title_rect)


# start experimental procedure
quit = False
instructions = True
n_run = 0
while not quit:
    level_done = False

    if instructions:
        display_instructions(screen)

    else:
        display_intertrial_screen(screen)

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if instructions:
                    level_done = run_visualization(surface=screen, scaling=scaling, tiny_visualization=False, FPS=FPS,
                                                   keyboard_input=True,
                                                   obstacles_lists_file=f'obstacles_list_0.csv',
                                                   drift_ranges_file=f'drift_ranges_0.csv',
                                                   trial=0, attempt=0, n_run=n_run, code=code)
                    if level_done:
                        instructions = False
                else:
                    random.shuffle(trials)
                    trial = trials[0]

                    level_done = run_visualization(surface=screen, scaling=scaling, tiny_visualization=False, FPS=FPS,
                                                   keyboard_input=True,
                                                   obstacles_lists_file=f'obstacles_list_{trial}.csv',
                                                   drift_ranges_file=f'drift_ranges_{trial}.csv',
                                                   trial=trial, attempt=attempt_dict[trial]+1, n_run=n_run, code=code)
                    n_run += 1

                    if level_done:  # if level was successfully solved, it won't be played again
                        trials.remove(trial)
                    else:
                        attempt_dict[trial] += 1
                        if attempt_dict[trial] >= max_attempts:  # if max_attempts reached, level won't be played again
                            trials.remove(trial)

                    if len(trials) < 1:  # if no level are left to play -> quit
                        quit = True

# print(attempt_dict)
pygame.quit()
