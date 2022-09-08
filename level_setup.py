import pygame
import time
from comets import Comet
from player import Player
from walls import Wall
from drift_tiles import DriftTile


class Level:
    def __init__(self, wall_list, obstacles_list, player_starting_position, drift_ranges, screen, scaling, tiny_vis=False):

        # level_setup
        self.display_surface = screen
        self.setup_level(wall_list, obstacles_list, player_starting_position, drift_ranges, scaling, tiny_vis)

    def setup_level(self, wall_list, obstacles_list, player_starting_position, drift_ranges, scaling, tiny_vis):
        self.walls = pygame.sprite.Group()
        self.comets = pygame.sprite.Group()
        self.drift_tiles = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

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
        
        player_sprite = Player(player_starting_position, scaling, tiny_vis)
        self.player.add(player_sprite)

        for i in range(len(drift_ranges)):
            drift_info = drift_ranges[i]  # drift_info[0]: y_start, [1]: y_end, [2]: direction
            drift_tile = DriftTile(drift_info[0], drift_info[1], drift_info[2])
            self.drift_tiles.add(drift_tile)

    def check_for_collision(self):
        player = self.player.sprite

        for sprite in self.comets.sprites():
            if sprite.rect.colliderect(player.rect):  # check for player-comet collision
                player.crashed = True
                player.image.fill('green') # for debugging

    def check_for_drift(self):
        player = self.player.sprite
        player.drift.x = 0
        for sprite in self.drift_tiles.sprites():
            if sprite.rect.left > player.rect.right:  # if drift.tile is right from player.tile than drift to left
                if player.rect.top in range(sprite.rect.top, sprite.rect.bottom):
                    player.drift.x = -1/2  # - imposes drift to the left that is 1/2 of normal movement
                    # player.image.fill("blue")  # for debugging
                elif player.rect.bottom in range(sprite.rect.top, sprite.rect.bottom):
                    player.drift.x = -1/2
                    # player.image.fill("yellow")  # for debugging
            elif sprite.rect.right < player.rect.left:  # if drift.tile is left from player.tile than drift to right
                if player.rect.top in range(sprite.rect.top, sprite.rect.bottom):
                    player.drift.x = 1/2  # imposes drift to the right that is 1/2 of normal movement
                    # player.image.fill("blue")  # for debugging
                elif player.rect.bottom in range(sprite.rect.top, sprite.rect.bottom):
                    player.drift.x = 1/2
                    # player.image.fill("yellow")  # for debugging
        
    def run(self, player_position, scaling, tiny_visualization=False, keyboard_input=False):

        # level tiles
        if not tiny_visualization:
            self.comets.update(scaling)
            self.walls.update(scaling)
            self.drift_tiles.update(scaling)

        # draw comets and tiles
        self.comets.draw(self.display_surface)
        self.walls.draw(self.display_surface)
        self.drift_tiles.draw(self.display_surface)

        # agent
        self.player.update(player_position, scaling, keyboard_input)
        self.player.draw(self.display_surface)
