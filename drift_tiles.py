import pygame
import os
import random
from config import observation_space_size_x, drift_tile_x_size, scaling, edge


class DriftTile(pygame.sprite.Sprite):
    def __init__(self, y_start, y_end, direction):
        """
        :param y_pos: position on level y-axis of drift tile
        :param size:
        """
        super().__init__()
        # drifttiles will be displayed as red rectangles
        self.y_range = y_end - y_start
        self.image = pygame.Surface((drift_tile_x_size*scaling, self.y_range))
        self.image.fill('red')
        # imposed drift by tile
        self.direction = direction
        # position of drift sprite
        self.y_pos = y_start
        # x_pos depends on direction (drift to right=tile is visualized to the left and vice versa)
        if self.direction == 0:  # leftwards drift visualized on right edge
            self.x_pos = observation_space_size_x*scaling + edge*scaling + (1/2*edge*scaling)
        elif self.direction == 2:
            self.x_pos = 1/2*edge*scaling
        pos = [self.x_pos, self.y_pos]
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, scaling):
        self.rect.y -= (1*scaling)
