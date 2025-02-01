import pygame
import numpy as np
import pandas as pd
import random
from ingame_objects.comets import Comet
from ingame_objects.player import Player
from ingame_objects.walls import Wall
from ingame_objects.drift_tiles import DriftTile
from ingame_objects.particles import Particle
from ingame_objects.lines import Line
from config import *

### Both used in same line
from helper_functions import degree_to_pixel #NOTE: used in repo
from draw_transparent_shapes import draw_rect_alpha, draw_polygon_alpha, draw_circle_alpha #NOTE: used in repo, see other notes
###

import warnings
warnings.filterwarnings(action="ignore", category=FutureWarning)


import os
import datetime

import actr.rpc_interface
import json
from actr.socket_manager import move_socket

#SHM
import ctypes
import mmap


libc = ctypes.CDLL("libc.so.6") 
shm_open = libc.shm_open # CDLL function to create/open POSIX shared memory objects 
shm_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
shm_open.restype = ctypes.c_int

shm_unlink = libc.shm_unlink
shm_unlink.argtypes = [ctypes.c_char_p]                     
shm_unlink.restype = ctypes.c_int
O_CREAT = os.O_CREAT
O_RDWR = os.O_RDWR
S_IRWXU = 0o700                         


# Shared Memory for pixels of environment
shm_name = b"/compas_shared_memory"
size1 = 840 * 1334  # Size of the memory to be mapped

# Create or open the shared memory object
fd = shm_open(shm_name, O_CREAT | O_RDWR, S_IRWXU)
if fd < 0:
    raise OSError("Failed to create shared memory object")

# Set the size of the shared memory object
if libc.ftruncate(fd, size1) != 0:
    raise OSError("Failed to set size of shared memory object")

# Memory map the shared memory object
mm = mmap.mmap(fd, size1)


# Shared Memory for player sprite rect x
shm_name2 = b"/compas_shared_memory_player"
size2 = 4  # Size of the memory to be mapped


# Create or open the shared memory object
fd2 = shm_open(shm_name2, O_CREAT | O_RDWR, S_IRWXU)
if fd2 < 0:
    raise OSError("Failed to create shared memory object")

# Set the size of the shared memory object
if libc.ftruncate(fd2, size2) != 0:
    raise OSError("Failed to set size of shared memory object")

# Memory map the shared memory object
mm2 = mmap.mmap(fd2, size2)


# Shared memory for reference point tuple
shm_name3 = b"/compas_shared_memory_reference"
size3 = 16
# Create or open the shared memory object
fd3 = shm_open(shm_name3, O_CREAT | O_RDWR, S_IRWXU)
if fd3 < 0:
    raise OSError("Failed to create shared memory object")

# Set the size of the shared memory object
if libc.ftruncate(fd3, size3) != 0:
    raise OSError("Failed to set size of shared memory object")
# Memory map the shared memory object
mm3 = mmap.mmap(fd3, size3)




display_keys = True
#NOTE: keyboard_input kann weg, ist auch im repo nicht mehr vorhanden, da agent autonom agieren soll.
class Level:
    def __init__(self, wall_list, obstacles_list, player_starting_position, drift_ranges, screen, scaling, code, FPS=30,
                 n_run=0, trial=0, attempt=0, tiny_vis=False, keyboard_input=False, input_noise_magnitude=0,
                 input_noise_threshold=0, drift_enabled=False):

        # experiment information
        self.code = code

        # sense of control during level
        self.SoC = None

        # level_setup
        self.trial = trial
        self.attempt = attempt
        self.display_surface = screen
        self.level_size_y = 'undetermined'
        self.setup_level(wall_list, obstacles_list, player_starting_position, drift_ranges, drift_enabled, scaling,
                         tiny_vis, keyboard_input)
        # environment movement around agent
        self.direction = pygame.math.Vector2(0, 0)
        # environmentally imposed drift
        self.drift = pygame.math.Vector2(0, 0)
        # player input
        self.current_input = None  # None vs. 'Right' vs. 'Left'
        # total horizontal movement combined of agent imposed direction and environmentally imposed drift
        self.horizontal_movement = 0
        # transparency for keys being pressed
        self.transparency_left = 90
        self.transparency_right = 90

        # listing visible obstacles in every instance, as well as adjacent wall tiles and last wall tile positions
        self.visible_obstacles = []
        self.adjacent_wall_tiles_x_pos = []
        self.last_wall_pos = []

        # Whether drift tiles appear and actually impose drift depends on this variable
        self.drift_enabled = drift_enabled

        # threshold and magnitude for imposing input noise on agent (is updated by subtracting step size)
        self.input_noise_threshold = input_noise_threshold*scaling
        self.input_noise_magnitude = input_noise_magnitude # 0.5 or 1 
        self.input_noise_on = False

        # n_run indicating the number of trials after starting the program (used to differentiate data files)
        self.n_run = n_run

        # Collision threshold; number of frames with player colliding to stop game
        self.frames_collision_threshold = FPS / 10
        # frames with player colliding
        self.frames_with_collision = 0

        self.time_played = 0
        self.FPS = FPS
        self.level_done = False
        self.quit = False
        # threshold for replaying trial - if time_played above threshold => no replay
        self.replay_threshold = 1000  # 25; in s
        if 'training' in str(self.trial):  # TRY CONTAIN
            self.replay_threshold = 1000  # arbitrarily high threshold that is never reached

        # pandas Dataframe in which data of each frame will be stored
        self.columns = ['trial', 'attempt', 'time_played', 'level_size_y', 'player_pos', 'collision', 'current_input',
                        'drift_enabled', 'current_drift', 'level_done', 'input_noise_magnitude', 'input_noise_on',
                        'visible_obstacles', 'last_walls_tile', 'adjacent_wall_tiles_x_pos', 'visible_drift_tiles',
                        'SoC']

        self.data = pd.DataFrame(columns=self.columns)


    def setup_level(self, wall_list, obstacles_list, player_starting_position, drift_ranges, drift_enabled, scaling,
                    tiny_vis, keyboard_input):
        self.walls = pygame.sprite.Group()
        self.comets = pygame.sprite.Group()
        self.drift_tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.particles = pygame.sprite.Group()
        self.bottom_edge = pygame.sprite.GroupSingle()
        self.finish_line = pygame.sprite.GroupSingle()

        for i in range(1, len(wall_list) + 1):
            # left wall
            left_wall_x_pos = (wall_list[str(i)][0])
            left_wall = Wall((left_wall_x_pos, i * scaling), wall_size, scaling)
            # i*scaling will result in the correct y-coord of the wall

            # right wall
            right_wall_x_pos = (wall_list[str(i)][1])
            right_wall = Wall((right_wall_x_pos, i * scaling), wall_size, scaling)

            # add both walls to sprite group
            self.walls.add(left_wall, right_wall)

        # determine level_size_y based on walls
        last_wall_tile = self.walls.sprites()[-1]
        self.level_size_y = last_wall_tile.rect.y + wall_size * scaling

        for key in obstacles_list:
            comet_sprite = Comet((key['x'], key['y']), key['size'])  # arguments in Comet(): x-pos, y-pos, tile_size
            self.comets.add(comet_sprite)

        #if keyboard_input:
        player_appearance = [player_starting_position[0], (player_starting_position[1] - pre_trial_steps * scaling)]
        player_sprite = Player(player_appearance, agent_size_x, agent_size_y, scaling, tiny_vis)
        self.player.add(player_sprite)

        #NOTE: Im Repo ist if und else nicht vorhanden, sondern wie hier
        #else:
        #    player_sprite = Player(player_starting_position, agent_size_x, agent_size_y, scaling, tiny_vis)
        #    self.player.add(player_sprite)

        if drift_enabled:
            for i in range(len(drift_ranges)):
                drift_info = drift_ranges[i]
                # drift_info[0]: y_start, [1]: y_end, [2]: direction+magnitude, [3]: visibility
                drift_tile = DriftTile(drift_info[0], drift_info[1], drift_tile_size_x, observation_space_size_x, edge,
                                       drift_info[2], drift_info[3], scaling)
                self.drift_tiles.add(drift_tile)

        for _ in range(int(last_wall_tile.rect.y / scaling * 2.5)):
            x_pos = np.random.uniform(low=edge * scaling, high=level_size_x * scaling + edge * scaling, size=1)
            y_pos = np.random.uniform(low=0, high=self.level_size_y, size=1)
            particle_tile = Particle((x_pos[0], y_pos[0]), random.choice(particle_sizes), scaling)
            self.particles.add(particle_tile)

        # grey edge at bottom of screen limiting observation window (do NOT update in .run)
        bottom_edge_tile = Line([0, (observation_space_size_y - bottom_edge) * scaling],
                                [(level_size_x + 2 * edge) * scaling, bottom_edge * scaling])
        self.bottom_edge.add(bottom_edge_tile)

        finish_line_tile = Line(pos=[edge * scaling, last_wall_tile.rect.y],
                                size=[level_size_x * scaling, scaling], col="seagreen")
        self.finish_line.add(finish_line_tile)
            
        #NOTE: Here the code uses Action Planner i.e.
        #NOTE: probably just initialization, this is Level.setup_level(...) 
        #self.agent = ActionPlanner(free_parameters=parameters,
        #                           initial_position_x=self.player.sprite.rect.x + scaling,
        #                           observation_space_in_pixel=[observation_space_size_x*scaling, observation_space_size_y*scaling])
        #self.convolutionGranularity = int(self.agent.parameters['convolutionGranularity'])
        #NOTE: Approach to solve
        rect_x = np.array([player_sprite.rect.x], dtype=np.int32)  # rect.x as an array
        rect_x_bytes = rect_x.tobytes()  # Convert to bytes
        mm2[0:4] = rect_x_bytes

    def get_input(self):
        # input noise
        player = self.player.sprite
        input_noise = 0
        #NOTE: Here repo has:
        #self.agent.apply_motor_control()
        #self.current_input = self.agent.action



        # input noise magnitude can be any float which reflects the magnitude of actual displacement
        # at the end of the left or right step. The magnitude directly translates to the sd of the normal distribution
        # the displacement is sampled from.
        if player.rect.y > self.input_noise_threshold:
            self.input_noise_on = True
            mu = 0
            sigma = self.input_noise_magnitude
            input_noise = np.random.normal(mu, sigma, 1)
        else:
            self.input_noise_on = False
        #############################
        # reset transparency for keys
        self.transparency_left = 90
        self.transparency_right = 90

        message = actr.rpc_interface.receive(socket=move_socket)

        # Receive and post the appropriate key press events
        if message is not None and 'method' in message.keys() and 'params' in message.keys() and 'id' in message.keys():
            if message['method'] == 'evaluate':
                if message['params'][0] == "moveleft":
                    #pygame.event.post(pygame.event.Event(key=pygame.K_y))
                    self.direction.x = 1 + input_noise
                    print(f"Move left with: {self.direction.x}")
                    print("Should move left")
                    #pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_y))
                    response_message = {
                        "result": ["result"],
                        "error": None,
                        "id": message['id']
                    }
                    #print(response_message)
                    actr.rpc_interface.send(move_socket, json.dumps(response_message))

                elif message['params'][0] == "moveright":
                    #pygame.event.post(pygame.event.Event(key=pygame.K_m))
                    #pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_m))
                    self.direction = -1 + input_noise
                    response_message = {
                        "result": ["result"],
                        "error": None,
                        "id": message['id']
                    }
                    actr.rpc_interface.send(move_socket, json.dumps(response_message))
                else:
                    self.direction.x = 0
                    print(f"Reset direction self.direction.x")

        # Handle the event loop
        """if self.agent.action == 'Right':
        self.direction.x = -1 + input_noise
        self.transparency_right = 150
        elif self.agent.action == 'Left':
        self.direction.x = 1 + input_noise
        self.transparency_left = 150
        else:  # self.agent.action is None
        self.direction.x = 0
        """

    def update(self):

        reference_point = (self.walls.sprites()[-2].rect.x + scaling, 208)
        
        # 532 * 394
        observation_space = reference_point[0], reference_point[1], 532, 394
        surface_subsection = self.display_surface.subsurface(observation_space)
        surface_array = np.transpose(pygame.surfarray.array_green(surface_subsection))
        surface_array[surface_array > 1] = 1
        

        # 
        size1 = 532 * 394


        # Convert the 2D array to bytes
        # green_array = green_array.flatten()
        green_bytes = surface_array.tobytes()
        

        # shm
        mm[0:len(green_bytes)] = green_bytes[:size1]

        rect_x = np.array([self.player.sprite.rect.x], dtype=np.int32)  # rect.x as an array
        rect_x_bytes = rect_x.tobytes()  # Convert to bytes
        mm2[0:4] = rect_x_bytes[0:len(rect_x_bytes)]


        #Transfer ref point to shared memory
        reference_point_bytes = np.array(reference_point).tobytes()

        mm3[0:len(reference_point_bytes)] = reference_point_bytes[:16]

        self.get_input()
        self.horizontal_movement = self.direction.x + self.drift.x  # compute horizontal movement with drift
        print(f"Update Horz. Movement with: {self.direction.x} and {self.drift.x}")




    def check_for_collision(self):
        player = self.player.sprite
        self.last_wall_pos = [self.walls.sprites()[-2].rect.x, self.walls.sprites()[-1].rect.x]

        # checking for general collision with any obstacles or walls or if spaceship jumped outside of game boarders;
        # collidelist will return index if collision and -1 if not
        if player.rect.collidelist(self.comets.sprites()) > -1 or player.rect.collidelist(self.walls.sprites()) > -1 or player.rect.left < self.last_wall_pos[0] or player.rect.right > self.last_wall_pos[1]:
            self.frames_with_collision += 1
        else:
            self.frames_with_collision = 0

        # checking for individual collisions:
        # # with obstacles
        # for sprite in self.comets.sprites():
        #     if sprite.rect.colliderect(player.rect):  # check for player-comet collision
        #         self.frames_with_collision += 1
        #
        # # with walls
        # for sprite in self.walls.sprites():
        #     if sprite.rect.colliderect(player.rect):  # check for player-wall collision
        #         self.currently_colliding = True
        #         self.frames_with_collision += 1

        # check for collision threshold of consecutive frames with collision
        if self.frames_with_collision > self.frames_collision_threshold:
            player.crashed = True

    def check_for_drift(self):
        player = self.player.sprite
        self.drift.x = 0

        for sprite in self.drift_tiles.sprites():
            if player.rect.top in range(sprite.rect.top, sprite.rect.bottom):
                self.drift.x = -sprite.direction
            elif player.rect.bottom in range(sprite.rect.top, sprite.rect.bottom):
                self.drift.x = -sprite.direction

    def get_soc_response(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            self.SoC = 1
        if keys[pygame.K_2]:
            self.SoC = 2
        if keys[pygame.K_3]:
            self.SoC = 3
        if keys[pygame.K_4]:
            self.SoC = 4
        if keys[pygame.K_5]:
            self.SoC = 5
        if keys[pygame.K_6]:
            self.SoC = 6
        if keys[pygame.K_7]:
            self.SoC = 7
        return self.SoC

    def get_data(self, scaling):

        frame_data = pd.DataFrame(columns=self.columns)

        player = self.player.sprite
        frame_data.at[0, 'player_pos'] = [player.rect.x, player.rect.y]  # player position will stay the same throughout
        frame_data.collision = player.crashed
        frame_data.current_input = self.current_input
        frame_data.drift_enabled = self.drift_enabled
        frame_data.current_drift = self.drift.x
        frame_data.level_done = self.level_done
        frame_data.input_noise_magnitude = self.input_noise_magnitude
        frame_data.input_noise_on = self.input_noise_on

        frame_data.time_played = self.time_played
        frame_data.trial = self.trial
        frame_data.attempt = self.attempt
        frame_data.level_size_y = self.level_size_y

        """
        Walls
        There has to be a better alternative instead of simply inserting all wall tiles into a list.
        Rather have one wall tile given and then distance to other wall? Or just distance from agent to wall left
        and right? - brainstorming

        wall narrowing start and wall narrowing complete + wall distant again?
        These would be the only interesting y coordinates

        # walls_narrow_start = ?  # walls start getting narrow (first step) y coord
        # walls_narrow_complete = ?  # walls reached narrowest point y coord
        # walls_wide_again = ?  # based on current_wall_distance='narrow', when walls get wide again
        # current_wall_distance = ['wide']  # on y coord of agent

        stupidly inserting all visible wall tiles in a list into frame_data
        # visible_walls = []
        # for sprite in self.walls.sprites():
        #     # checking for visibility by checking for y of sprite being between 0 and size of observation window
        #     if 0 <= sprite.rect.y <= observation_space_size_y * scaling:
        #         visible_walls.append([sprite.rect.x, sprite.rect.y])
        # frame_data.at[0, 'visible_walls'] = visible_walls
        """
        # inserting only last wall tile (bottom right of level) for later reconstruction of complete walls
        last_wall_tile = self.walls.sprites()[-1]
        frame_data.at[0, 'last_walls_tile'] = [last_wall_tile.rect.x, last_wall_tile.rect.y]

        # obstacles
        frame_data.at[0, 'visible_obstacles'] = self.visible_obstacles

        # drift
        visible_drift_tiles = []
        for sprite in self.drift_tiles.sprites():
            if 0 <= sprite.rect.y <= (observation_space_size_y - bottom_edge) * scaling:
                visible_drift_tiles.append([sprite.rect.x, sprite.rect.y])
        frame_data.at[0, 'visible_drift_tiles'] = visible_drift_tiles

        # append everything to pandas DataFrame
        self.data = pd.concat([self.data, frame_data], ignore_index=True)
        self.data.SoC = self.SoC

    def run(self, time_played, player_position, scaling, tiny_visualization=False, keyboard_input=False):

        self.time_played = time_played
        player = self.player.sprite

        # updating visible obstacles
        self.visible_obstacles = []
        for sprite in self.comets.sprites():
            if 0 <= sprite.rect.y <= (observation_space_size_y - bottom_edge) * scaling:
                self.visible_obstacles.append([sprite.rect.x, sprite.rect.y])
        # updating visible drift tiles
        self.visible_drift_tiles = []
        for sprite in self.drift_tiles.sprites():
            if 0 <= sprite.rect.y <= (observation_space_size_y - bottom_edge) * scaling:
                self.visible_drift_tiles.append([sprite.rect.x, sprite.rect.y])

        # updating adjacent wall tiles y pos (left wall, right wall)
        self.adjacent_wall_tiles_x_pos = [self.walls.sprites()[0].rect.x, self.walls.sprites()[1].rect.x]

        # check for level done: if player went over finish line => level_done
        finish_line = self.finish_line.sprites()[-1]
        if finish_line.rect.bottom < player.rect.top:  # (observation_space_size_y - bottom_edge) * scaling:
            self.level_done = True
            self.quit = True
            # write data of all frames to csv
            self.get_data(scaling)
            #self.data.to_csv(f'data/{self.code}_output_{self.convolutionGranularity}_{self.trial}_{self.n_run:0>2}.csv', sep=',', index=False)

        elif player.crashed:
            if self.time_played > self.replay_threshold:
                self.level_done = True
            self.quit = True
            # write data of all frames to csv
            self.get_data(scaling)
            #self.data.to_csv(f'data/{self.code}_output_{self.convolutionGranularity}_{self.trial}_{self.n_run:0>2}.csv', sep=',', index=False)
            #for every frame for each trial, buffer activity also
        else:
            self.level_done = False

            player.animate(self.current_input)

            if player.rect.y < player_position[1]:
                player.approach(velocity, scaling)
                pass
            if player.rect.y >= player_position[1]:
                # update sprite positions
                # update level tiles
                self.comets.update(velocity, scaling, self.horizontal_movement)
                self.walls.update(velocity, scaling, self.horizontal_movement)
                self.drift_tiles.update(velocity, scaling, self.horizontal_movement)
                self.particles.update(velocity, scaling, self.horizontal_movement)
                self.finish_line.update(velocity, scaling, self.horizontal_movement)
                print(self.horizontal_movement)
                print("Updated objects with horiz. movement")
                self.horizontal_movement = 0
                self.direction.x = 0
                # update action goal
                #self.agent.update_action_goal(velocity, scaling, self.horizontal_movement)

                # update input_noise threshold
                self.input_noise_threshold -= 1 * scaling * velocity  # same updating as for all in-game objects

            # check for collision
            self.check_for_collision()
            # check for drift
            self.check_for_drift()

            # draw sprites
            # draw comets and tiles
            self.particles.draw(self.display_surface)
            self.comets.draw(self.display_surface)
            self.walls.draw(self.display_surface)
            self.drift_tiles.draw(self.display_surface)
            self.finish_line.draw(self.display_surface)
            self.bottom_edge.draw(self.display_surface)
            # to display finish line when on screen but under bottom edge,
            # simply call draw method of buttom_edge.draw() AFTER finish_line.draw()

            self.update()

            # draw agent
            self.player.draw(self.display_surface)
            # draw transparent circle around action goal
            
            #NOTE: This happens in the repo
            #draw_circle_alpha(surface=self.display_surface, color=(255, 0, 0, 100), center=self.agent.action_goal, radius=degree_to_pixel(1))
            # draw fixated action goal
            #pygame.draw.circle(self.display_surface, (255, 0, 0), self.agent.action_goal, 2)
            # draw SoC indicators
            # low-level
            #pygame.draw.rect(self.display_surface, (50, 168, 82),
            #                 (player.rect.x + 2*scaling, player.rect.y - self.agent.LL_SoC * 2*scaling, scaling, self.agent.LL_SoC * 2*scaling))
            # high-level
            #pygame.draw.rect(self.display_surface, (232, 137, 12),
            #                 (player.rect.x + 3.1*scaling, player.rect.y - self.agent.HL_SoC * 2*scaling, scaling, self.agent.HL_SoC * 2*scaling))
            #NOTE: Previous note until here

            # draw keys
            if display_keys:
                # right key
                draw_rect_alpha(self.display_surface, (124, 252, 0, self.transparency_right), (160, 60, 90, 90))
                draw_polygon_alpha(self.display_surface, (255, 255, 255, self.transparency_right),
                                   [(240, 105), (170, 70), (170, 140)])
                # left key
                draw_rect_alpha(self.display_surface, (124, 252, 0, self.transparency_left), (60, 60, 90, 90))
                draw_polygon_alpha(self.display_surface, (255, 255, 255, self.transparency_left),
                                   [(70, 105), (140, 70), (140, 140)])

            self.get_data(scaling)

        return self.quit, self.level_done
