import pygame
import os
import random


class DriftTile(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        # drifttiles will be displayed as red rectangles
        self.image = pygame.Surface((size, size))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, scaling):
        self.rect.y -= (1*scaling)
