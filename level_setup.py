import pygame
import time
import numpy as np
import pandas as pd
import random
from comets import Comet
from player import Player
from walls import Wall
from drift_tiles import DriftTile
from particles import Particle
from lines import Line
from config import level_size_x, level_size_y, observation_space_size_y, velocity, particle_sizes, edge, N_particles, \
    pre_trial_steps, agent_size_x, agent_size_y, input_noise_threshold

from draw_transparent_shapes import draw_rect_alpha, draw_polygon_alpha, draw_circle_alpha

display_keys = False
input_noise_args = [None, "weak", "strong"]
input_noise_magnitude = random.choice(input_noise_args)
print(input_noise_magnitude)  # printing statement to check for drift after piloting


class Level:
    def __init__(self, wall_list, obstacles_list, player_starting_position, drift_ranges, screen, scaling,
                 tiny_vis=False, keyboard_input=False):

        # level_setup
        self.display_surface = screen
        self.setup_level(wall_list, obstacles_list, player_starting_position, drift_ranges, scaling,
                         tiny_vis, keyboard_input)
        # environment movement around agent
        self.direction = pygame.math.Vector2(0, 0)
        # environmentally imposed drift
        self.drift = pygame.math.Vector2(0, 0)
        # total horizontal movement combined of agent imposed direction and environmentally imposed drift
        self.horizontal_movement = 0
        # transparency for keys being pressed
        self.transparency_left = 90
        self.transparency_right = 90

        # threshold for imposing input noise on agent (will wander upwards)
        self.input_noise_threshold = input_noise_threshold

        self.n_run = 0
        self.time_played = 0
        self.level_done = False

        # pandas Dataframe in which data of each frame will be stored
        self.columns = ['time_played', 'player_pos', 'collision', 'current_direction', 'current_drift', 'level_done',
                        'input_noise_magnitude', 'input_noise_threshold', 'visible_obstacles', 'visible_drift_tiles']
        self.data = pd.DataFrame(columns=self.columns)

    def setup_level(self, wall_list, obstacles_list, player_starting_position, drift_ranges, scaling,
                    tiny_vis, keyboard_input):
        self.walls = pygame.sprite.Group()
        self.comets = pygame.sprite.Group()
        self.drift_tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.particles = pygame.sprite.Group()

        for i in range(1, len(wall_list) + 1):
            # left wall
            left_wall_x_pos = (wall_list[str(i)][0])
            left_wall = Wall((left_wall_x_pos, i * scaling), scaling)
            # i*scaling will result in the correct y-coord of the wall

            # right wall
            right_wall_x_pos = (wall_list[str(i)][1])
            right_wall = Wall((right_wall_x_pos, i * scaling), scaling)

            # add both walls to sprite group
            self.walls.add(left_wall, right_wall)

        for key in obstacles_list:
            comet_sprite = Comet((key['x'], key['y']), key['size'])  # arguments in Comet(): x-pos, y-pos, tile_size
            self.comets.add(comet_sprite)

        if keyboard_input:
            player_appearance = [player_starting_position[0], (player_starting_position[1] - pre_trial_steps * scaling)]
            player_sprite = Player(player_appearance, scaling, tiny_vis)
            self.player.add(player_sprite)

        else:
            player_sprite = Player(player_starting_position, scaling, tiny_vis)
            self.player.add(player_sprite)

        for i in range(len(drift_ranges)):
            drift_info = drift_ranges[i]  # drift_info[0]: y_start, [1]: y_end, [2]: direction
            if drift_info[0] < (level_size_y * scaling) * 2 / 3:  # have no drift_tiles in the last third of the level
                drift_tile = DriftTile(drift_info[0], drift_info[1], drift_info[2], scaling)
                self.drift_tiles.add(drift_tile)

        for _ in range(N_particles):
            x_pos = np.random.uniform(low=edge * scaling, high=level_size_x * scaling + edge * scaling, size=1)
            y_pos = np.random.uniform(low=0, high=level_size_y * scaling, size=1)
            particle_tile = Particle((x_pos[0], y_pos[0]), random.choice(particle_sizes), scaling)
            self.particles.add(particle_tile)

    def get_input(self):
        # input noise
        player = self.player.sprite
        input_noise = 0
        # input noise magnitude can be None = 0 vs. weak vs. strong which reflects the magnitude of actual displacement
        # at the end of the left or right step. The magnitude directly translates to the sd of the normal distribution
        # the displacement is sampled from.
        if player.rect.y > self.input_noise_threshold:
            mu = 0
            if input_noise_magnitude is None:
                pass
            elif input_noise_magnitude == "weak":
                sigma = 0.5  # mean and standard deviation
                input_noise = np.random.normal(mu, sigma, 1)
            elif input_noise_magnitude == "strong":
                sigma = 1
                input_noise = np.random.normal(mu, sigma, 1)
        #############################
        # reset transparency for keys
        self.transparency_left = 90
        self.transparency_right = 90

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:  # K_m
            self.direction.x = -1 + input_noise
            self.transparency_right = 150
        elif keys[pygame.K_LEFT]:  # K_y
            self.direction.x = 1 + input_noise
            self.transparency_left = 150
        else:
            self.direction.x = 0

    def update(self):
        self.get_input()
        self.horizontal_movement = self.direction.x + self.drift.x  # compute horizontal movement with drift

    def check_for_collision(self):
        player = self.player.sprite
        # player.image.fill('green')  # for debugging

        # obstacles
        for sprite in self.comets.sprites():
            if sprite.rect.colliderect(player.rect):  # check for player-comet collision
                player.crashed = True
                # player.image.fill('red')  # for debugging

        # walls
        for sprite in self.walls.sprites():
            if sprite.rect.colliderect(player.rect):  # check for player-wall collision
                player.crashed = True
                # player.image.fill('red')  # for debugging

    def check_for_drift(self):
        player = self.player.sprite
        self.drift.x = 0
        for sprite in self.drift_tiles.sprites():
            if sprite.rect.left > player.rect.right:  # if drift.tile is right from player.tile than drift to left
                if player.rect.top in range(sprite.rect.top, sprite.rect.bottom):
                    self.drift.x = 1 / 2  # - imposes drift to the left that is 1/2 of normal movement
                    # player.image.fill("blue")  # for debugging
                elif player.rect.bottom in range(sprite.rect.top, sprite.rect.bottom):
                    self.drift.x = 1 / 2
                    # player.image.fill("yellow")  # for debugging
            elif sprite.rect.right < player.rect.left:  # if drift.tile is left from player.tile than drift to right
                if player.rect.top in range(sprite.rect.top, sprite.rect.bottom):
                    self.drift.x = -1 / 2  # imposes drift to the right that is 1/2 of normal movement
                    # player.image.fill("blue")  # for debugging
                elif player.rect.bottom in range(sprite.rect.top, sprite.rect.bottom):
                    self.drift.x = -1 / 2
                    # player.image.fill("yellow")  # for debugging

    def get_data(self, scaling):

        frame_data = pd.DataFrame(columns=self.columns)

        player = self.player.sprite
        frame_data.at[0, 'player_pos'] = [player.rect.x, player.rect.y]  # player position will stay the same throughout
        frame_data.collision = player.crashed
        frame_data.at[0, 'current_direction'] = self.direction
        frame_data.at[0, 'current_drift'] = self.drift
        frame_data.level_done = self.level_done
        frame_data.input_noise_magnitude = input_noise_magnitude
        frame_data.input_noise_threshold = input_noise_threshold

        frame_data.time_played = self.time_played

        # walls
        # There has to be a better alternative instead of simply inserting all wall tiles into a list.
        # Rather have one wall tile given and then distance to other wall? Or just distance from agent to wall left
        # and right? - brainstorming

        # visible_walls = []
        # for sprite in self.walls.sprites():
        #     # checking for visibility by checking for y of sprite being between 0 and size of observation window
        #     if 0 <= sprite.rect.y <= observation_space_size_y * scaling:
        #         visible_walls.append(np.array([sprite.rect.x, sprite.rect.y]))
        # frame_data.visible_walls = np.array([visible_walls])

        # obstacles
        visible_obstacles = []
        for sprite in self.comets.sprites():
            if 0 <= sprite.rect.y <= observation_space_size_y * scaling:
                visible_obstacles.append(np.array([sprite.rect.x, sprite.rect.y]))
        frame_data.at[0, 'visible_obstacles'] = [visible_obstacles]

        # drift
        visible_drift_tiles = []
        for sprite in self.drift_tiles.sprites():
            if 0 <= sprite.rect.y <= observation_space_size_y * scaling:
                visible_drift_tiles.append(np.array([sprite.rect.x, sprite.rect.y]))
        frame_data.at[0, 'visible_drift_tiles'] = [visible_drift_tiles]

        # append everything to pandas DataFrame
        # print(frame_data)
        self.data = pd.concat([self.data, frame_data], ignore_index=True)

    def run(self, time_played, player_position, scaling, tiny_visualization=False, keyboard_input=False):

        self.time_played = time_played
        player = self.player.sprite

        if not tiny_visualization and keyboard_input:
            player.animate(self.direction.x)

        if keyboard_input:
            self.update()
        else:
            self.player.update(player_position, scaling, keyboard_input)

        if keyboard_input and player.rect.y < player_position[1]:
            player.approach(velocity, scaling)
            pass
        if not tiny_visualization and player.rect.y >= player_position[1]:
            # update sprite positions
            # update level tiles
            self.comets.update(velocity, scaling, self.horizontal_movement)
            self.walls.update(velocity, scaling, self.horizontal_movement)
            self.drift_tiles.update(velocity, scaling, self.horizontal_movement)
            self.particles.update(velocity, scaling, self.horizontal_movement)

            # update input_noise threshold
            self.input_noise_threshold -= 1 * scaling * velocity  # same updating as for all in-game objects

        # check for level done: if last sprite is in observation_space => level_done
        sprite = self.walls.sprites()[-1]
        if sprite.rect.bottom < observation_space_size_y * scaling:
            self.level_done = True
            # write data of all frames to csv
            self.data.to_csv(f'data/data_{self.n_run}.csv', decimal=',')
            self.n_run += 1
        else:
            self.level_done = False

        if keyboard_input:  # only needed if player is controlling spaceship
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

        # draw agent
        self.player.draw(self.display_surface)

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

        return self.level_done
