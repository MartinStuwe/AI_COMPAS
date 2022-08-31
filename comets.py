import pygame
import os
import random
from config import scaling


class Comet(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        # actual comet image which will be drawn on rectangular surface of comet
        self.image = pygame.image.load(os.path.join('Assets/comets', 'comet_master.png')).convert_alpha()
        self.random_angle = random.choice([0, 90, 180, 270])  # items of list are random angles in 90 degree steps
        self.image = pygame.transform.rotate(pygame.transform.scale(self.image, (size, size)), angle=self.random_angle)
        self.rect = self.image.get_rect(topleft=pos)

    def update(self):
        self.rect.y -= (1*scaling)
