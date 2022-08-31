import pygame
from comets import Comet
from player import Player
from config import scaling


class Level:
    def __init__(self, obstacles_list, player_starting_position, screen):

        # level_setup
        self.display_surface = screen
        self.setup_level(obstacles_list, player_starting_position)

    def setup_level(self, obstacles_list, player_starting_position):
        self.comets = pygame.sprite.Group()
        self.player = pygame.sprite.GroupSingle()

        for key in obstacles_list:
            comet_sprite = Comet((key['x'], key['y']), key['size'])  # arguments in Comet(): x-pos, y-pos, tile_size
            self.comets.add(comet_sprite)

        player_sprite = Player(starting_pos=player_starting_position)
        self.player.add(player_sprite)

    def run(self, player_position):

        # level tiles
        self.comets.update()
        self.comets.draw(self.display_surface)
        # later wall tiles & drift tiles

        # agent
        self.player.update(player_position)
        self.player.draw(self.display_surface)
