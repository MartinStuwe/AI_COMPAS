import pygame
import os
from config import agent_size_x, agent_size_y, scaling


class Player(pygame.sprite.Sprite):
    def __init__(self, starting_pos):
        super().__init__()
        # actual image which will be drawn on player rectangle
        self.image = pygame.image.load(os.path.join('Assets/spaceship', 'spaceship_master.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (agent_size_x*scaling, agent_size_y*scaling))
        #self.image = pygame.Surface((agent_size_x, agent_size_y))
        #self.image.fill('green')
        # rectangular surface of the player
        self.rect = self.image.get_rect(topleft=starting_pos)

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        self.velocity = 5  # testing out various player left & right movement velocities
        # imposed movement
        self.drift = pygame.math.Vector2(0, 0)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self, pos):
        # self.get_input()  # in an experimental run: player.get_input() & direction.y = config.fall_velocity
        self.rect = self.image.get_rect(topleft=pos)
