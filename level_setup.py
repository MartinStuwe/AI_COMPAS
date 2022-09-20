import pygame
import time
import numpy as np
import random
from comets import Comet
from player import Player
from walls import Wall
from drift_tiles import DriftTile
from particles import Particle
from config import level_size_x, level_size_y, particle_sizes, edge, N_particles, pre_trial_steps

from draw_transparent_shapes import draw_rect_alpha, draw_polygon_alpha


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
        # transparency for buttons being pressed
        self.transparency_left = 90
        self.transparency_right = 90

    def setup_level(self, wall_list, obstacles_list, player_starting_position, drift_ranges, scaling,
                    tiny_vis, keyboard_input):
        self.walls = pygame.sprite.Group()
        self.comets = pygame.sprite.Group()
        self.drift_tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()
        self.particles = pygame.sprite.Group()

        for i in range(1, len(wall_list)+1):
            # left wall
            left_wall_x_pos = (wall_list[str(i)][0])
            left_wall = Wall((left_wall_x_pos, i*scaling), scaling)
            # i*scaling will result in the correct y-coord of the wall

            # right wall
            right_wall_x_pos = (wall_list[str(i)][1])
            right_wall = Wall((right_wall_x_pos, i*scaling), scaling)

            # add both walls to sprite group
            self.walls.add(left_wall, right_wall)

        for key in obstacles_list:
            comet_sprite = Comet((key['x'], key['y']), key['size'])  # arguments in Comet(): x-pos, y-pos, tile_size
            self.comets.add(comet_sprite)

        if keyboard_input:
            player_appearance = [player_starting_position[0], (player_starting_position[1]-pre_trial_steps*scaling)]
            player_sprite = Player(player_appearance, scaling, tiny_vis)
            self.player.add(player_sprite)
        else:
            player_sprite = Player(player_starting_position, scaling, tiny_vis)
            self.player.add(player_sprite)

        for i in range(len(drift_ranges)):
            drift_info = drift_ranges[i]  # drift_info[0]: y_start, [1]: y_end, [2]: direction
            drift_tile = DriftTile(drift_info[0], drift_info[1], drift_info[2], scaling)
            self.drift_tiles.add(drift_tile)

        for _ in range(N_particles):
            x_pos = np.random.uniform(low=edge*scaling, high=level_size_x*scaling + edge*scaling, size=1)
            y_pos = np.random.uniform(low=0, high=level_size_y*scaling, size=1)
            particle_tile = Particle((x_pos[0], y_pos[0]), random.choice(particle_sizes), scaling)
            self.particles.add(particle_tile)

    def get_input(self):
        # input noise
        # mu, sigma = 0, 0.5  # mean and standard deviation
        # input_noise = np.random.normal(mu, sigma, 1)
        self.transparency_left = 90
        self.transparency_right = 90

        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:  # K_m
            self.direction.x = -1  # + input_noise
            self.transparency_right = 150
        elif keys[pygame.K_LEFT]:  # K_y
            self.direction.x = 1  # + input_noise
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
                    self.drift.x = 1/2  # - imposes drift to the left that is 1/2 of normal movement
                    # player.image.fill("blue")  # for debugging
                elif player.rect.bottom in range(sprite.rect.top, sprite.rect.bottom):
                    self.drift.x = 1/2
                    # player.image.fill("yellow")  # for debugging
            elif sprite.rect.right < player.rect.left:  # if drift.tile is left from player.tile than drift to right
                if player.rect.top in range(sprite.rect.top, sprite.rect.bottom):
                    self.drift.x = -1/2  # imposes drift to the right that is 1/2 of normal movement
                    # player.image.fill("blue")  # for debugging
                elif player.rect.bottom in range(sprite.rect.top, sprite.rect.bottom):
                    self.drift.x = -1/2
                    # player.image.fill("yellow")  # for debugging
        
    def run(self, player_position, scaling, tiny_visualization=False, keyboard_input=False):

        player = self.player.sprite
        if not tiny_visualization and keyboard_input:
            player.animate(self.direction.x)

        if keyboard_input:
            self.update()
        else:
            self.player.update(player_position, scaling, keyboard_input)

        if keyboard_input and player.rect.y < player_position[1]:
            player.approach(scaling)
        if not tiny_visualization and player.rect.y >= player_position[1]:
            # update sprite positions
            # update level tiles
            self.comets.update(scaling, self.horizontal_movement)
            self.walls.update(scaling, self.horizontal_movement)
            self.drift_tiles.update(scaling, self.horizontal_movement)
            self.particles.update(scaling, self.horizontal_movement)

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
        # right key
        draw_rect_alpha(self.display_surface, (124, 252, 0, self.transparency_right), (160, 60, 90, 90))
        draw_polygon_alpha(self.display_surface, (255, 255, 255, self.transparency_right),
                           [(240, 105), (170, 70), (170, 140)])
        # left key
        draw_rect_alpha(self.display_surface, (124, 252, 0, self.transparency_left), (60, 60, 90, 90))
        draw_polygon_alpha(self.display_surface, (255, 255, 255, self.transparency_left),
                           [(70, 105), (140, 70), (140, 140)])
