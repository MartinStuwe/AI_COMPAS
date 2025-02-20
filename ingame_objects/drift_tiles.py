import pygame
import os
import random

import actr.rpc_interface
from actr.socket_manager import drift_socket


class DriftTile(pygame.sprite.Sprite):
    global_id_counter = 0
    def __init__(self, y_start, y_end, size_x, obs_space_x, edge, direction, visibility, scaling):
        """
        :param y_start: position on level y-axis of drift tile
        :param y_end: end position on level y_axis of drift tile
        :param direction: direction of imposed drift; as well as magnitude. The higher the value the weaker the drift
        :param scaling: scaling variable to compute final
        """
        super().__init__()
        # drift tiles will be displayed as red rectangles
        self.y_range = y_end - y_start
        self.image = pygame.Surface((size_x * scaling, self.y_range))
        if visibility:
            self.image.fill('red')
        else:
            self.image.fill('black')
        # imposed drift by tile
        self.direction = 1/direction
        # position of drift sprite
        self.y_pos = y_start
        # x_pos depends on direction (drift to right=tile is visualized to the left and vice versa)
        # scaling is used to compute final x_pos
        if self.direction < 0:  # leftwards drift visualized on right edge
            self.x_pos = obs_space_x*scaling + edge*scaling + (1/6*edge*scaling) - size_x*scaling
        elif self.direction > 0:  # rightwards drift visualized on left edge
            self.x_pos = edge*scaling - (1/6*edge*scaling)
        pos = [self.x_pos, self.y_pos]
        self.rect = self.image.get_rect(topleft=pos)

        global global_id_counter
        self.id = DriftTile.global_id_counter + 1
        DriftTile.global_id_counter += 1

    def update(self, speed, scaling, horizontal_movement):
        # vertical movement
        self.rect.y -= (1*scaling) * speed
        # horizontal movement
        self.rect.x += horizontal_movement * scaling * speed

    def update_visicon(self): 
        message = f"{{\"method\": \"evaluate\", \"params\":[\"add-visicon-features\", \"compas-model\", [\"screen-x\", {self.rect.x}, \"screen-y\", {self.rect.y}, \"drift-id\", {self.id}]], \"id\": 4}}"

        actr.rpc_interface.communicate_socket(sock=drift_socket, message=message)