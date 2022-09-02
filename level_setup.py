import pygame
from comets import Comet
from player import Player
from walls import Wall


class Level:
    def __init__(self, wall_list, obstacles_list, player_starting_position, screen, scaling):

        # level_setup
        self.display_surface = screen
        self.setup_level(wall_list, obstacles_list, player_starting_position, scaling)

    def setup_level(self, wall_list, obstacles_list, player_starting_position, scaling):
        self.walls = pygame.sprite.Group()
        self.comets = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        for i in range(1, len(wall_list)+1):
            # left wall
            left_wall_x_pos = (wall_list[str(i)][0])
            left_wall = Wall((left_wall_x_pos, i), scaling)
            print('left_wall:', left_wall_x_pos, i)

            # right wall
            right_wall_x_pos = (wall_list[str(i)][1])
            right_wall = Wall((right_wall_x_pos, i), scaling)
            print('right_wall:', right_wall_x_pos, i)

            # add both walls to sprite group
            self.walls.add(left_wall, right_wall)
            print(len(self.walls))

        for key in obstacles_list:
            comet_sprite = Comet((key['x'], key['y']), key['size'])  # arguments in Comet(): x-pos, y-pos, tile_size
            self.comets.add(comet_sprite)
        
        player_sprite = Player(player_starting_position, scaling)
        self.player.add(player_sprite)

    def run(self, player_position, scaling, tiny_visualization=False):

        # level tiles
        if not tiny_visualization:
            self.comets.update(scaling)
            self.walls.update(scaling)

        # draw comets and tiles
        self.comets.draw(self.display_surface)
        self.walls.draw(self.display_surface)

        # agent
        self.player.update(player_position)
        self.player.draw(self.display_surface)
