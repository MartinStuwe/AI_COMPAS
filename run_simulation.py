import pygame.display
import time
import random
import os
import itertools
from main import run_visualization
from displays import *
from config import observation_space_size_x, observation_space_size_y, scaling, edge


# participant code
# code = input('Enter code: ')
code = 'simulating_action_goals'

# initialize pygame
# how many frames per second
FPS = 60

# pygame general setup
pygame.init()

# initialize pygame display
screen_width = (observation_space_size_x + (2 * edge)) * scaling
screen_height = observation_space_size_y * scaling
screen = pygame.display.set_mode((screen_width, screen_height))  # ,pygame.FULLSCREEN vs. pygame.RESIZABLE

# initialize experimental procedure
# N_trials = 6  # for each trial there must be a drift_ranges, object_list, and walls_dict file in the logs folder
# trials = list(range(1, N_trials + 1))  # end +1 due to python stopping before processing last entry
trials = [1, 2, 3, 4, 5, 6]  # simply stating levels-to-be-played is also possible
# trials = [3]

# drift enabled
# drift_enabled_args = [True, False]
drift_enabled_args = [False]

# input noise
# input_noise_args = [0, 0.5, 1, 1.5, 2]
input_noise_args = [0, 0.5, 1]

# create list of all possible combinations of level and control manipulations
args_list = [trials, drift_enabled_args, input_noise_args]
arg_combs = list(itertools.product(*args_list))
# order of args:
# 0: trial; 1: drift; 2: input noise

# attempts_dict for monitoring attempts per trial
attempt_dict = dict.fromkeys(arg_combs, 0)  # every trial at 0 attempts
list_of_attempt_dict_keys = list(attempt_dict.keys())
# list_of_attempt_dict_keys is our loop object. We will remove trials from here when they are attempted 3 times already
# or have been solved completely

max_attempts = 3  # maximum number of attempts given to solve trial



from actr import rpc_interface
from actr.socket_manager import comet_socket, move_socket
# Define the chunk description according to the syntax
import json

# Define the chunk name and attributes correctly
chunk_name = "game-screen-size"
chunk_type = "screen-size"
slots = {
    "height": screen_height,
    "width": screen_width
}

# Create the chunk description
chunk_description = [
    chunk_name,
    "isa", chunk_type,  # The chunk type
]

# Add the slot-value pairs
for slot_name, value in slots.items():
    chunk_description.append(slot_name)
    chunk_description.append(value)

# Convert the chunk description to a JSON string
chunk_description_json = json.dumps(chunk_description)

# Construct the final message
message = f"""
{{
    "method": "evaluate",
    "params": [
        "add-dm",
        "compas-model",
        {chunk_description_json}
    ],
    "id": 1
}}
"""

# Send the message via the RPC interface
received = rpc_interface.communicate_socket(sock=comet_socket, message=message)

# Print the received response
print(f"received: {received}")

# Pass moveleft command
message2 = '{"method": "add", "params":["moveleft", "moveleft", "this documents moveleft"], "id": 1}'
print(f"message2: {message2}")
#socket.setblocking(False)
received = rpc_interface.communicate_socket(move_socket, message2)
print(f"received: {received}")


# Pass moveright command
message2 = '{"method": "add", "params":["moveright", "moveright", "this documents moveright"], "id": 2}'
print(message2)
received = rpc_interface.communicate_socket(move_socket, message2)
print(f"received: {received}")


import numpy as np
from multiprocessing import shared_memory


shared_array = np.array([1, 2, 3, 4], dtype=np.int64)
shm = shared_memory.SharedMemory(create=True, size=shared_array.nbytes)

buffer = np.ndarray(shared_array.shape, dtype=shared_array.dtype, buffer=shm.buf)
buffer[:] = shared_array[:]

print("name of shared memory: " + shm.name)

level_done = False
n_run = 0
while not quit:

    if level_done:
        display_intertrial_screen(screen)
    else:
        display_intertrial_screen_after_crash(screen)

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit = True
        else:
            while len(list_of_attempt_dict_keys) > 1:  # play as long as there are levels...
                random.shuffle(list_of_attempt_dict_keys)
                trial = list_of_attempt_dict_keys[0]

                level_done = run_visualization(surface=screen, scaling=scaling, FPS=FPS,
                                               obstacles_lists_file=f'object_list_{trial[0]}.csv',
                                               drift_ranges_file=f'drift_ranges_{trial[0]}.csv',
                                               wall_list_file=f'walls_dict_{trial[0]}.csv',
                                               input_noise_magnitude=trial[2],
                                               drift_enabled=trial[1],
                                               trial=trial[0],
                                               attempt=attempt_dict[trial]+1,
                                               n_run=n_run, code=code)
                n_run += 1
                attempt_dict[trial] += 1

                if level_done:  # if level was successfully solved, it won't be played again
                    list_of_attempt_dict_keys.remove(trial)
                else:
                    if attempt_dict[trial] >= max_attempts:  # if max_attempts reached, level won't be played again
                        list_of_attempt_dict_keys.remove(trial)
            # ...otherwise quit
            quit = True

# print(attempt_dict)
pygame.quit()

shm.close()
shm.unlink()