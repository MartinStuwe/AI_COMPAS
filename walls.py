import pygame
from config import wall_size


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos, scaling):
        super().__init__()
        self.image = pygame.Surface((wall_size * scaling, wall_size * scaling))
        self.image.fill('white')
        self.rect = self.image.get_rect(topleft=pos)

    def update(self, scaling):
        self.rect.y -= (1*scaling)
