import pygame
import os
from config import agent_size_x, agent_size_y


class Player(pygame.sprite.Sprite):
    def __init__(self, starting_pos, scaling, tiny_vis=False):
        super().__init__()
        # actual image which will be drawn on player rectangle
        self.image = pygame.image.load(os.path.join('assets/spaceship', 'spaceship_master.png')).convert_alpha()
        self.image = pygame.transform.scale(self.image, (agent_size_x*scaling, agent_size_y*scaling))
        if tiny_vis:
            self.image = pygame.Surface((agent_size_x*scaling, agent_size_y*scaling))
            self.image.fill('green')
        # rectangular surface of the player
        self.rect = self.image.get_rect(topleft=starting_pos)

        # player movement
        self.direction = pygame.math.Vector2(0, 0)
        # self.velocity = 5  # testing out various player left & right movement velocities
        # imposed movement
        self.drift = pygame.math.Vector2(0, 0)
        self.crashed = False

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self, player_position, scaling, keyboard_input=False):
        if keyboard_input:
            self.get_input()
            player_horizontal_movement = self.direction.x + self.drift.x  # compute horizontal movement with drift
            self.rect.x += player_horizontal_movement * scaling  # apply horizontal drift
        else:
            self.rect = self.image.get_rect(topleft=player_position)

    def approach(self, scaling):
        """
        approaching movement of agent at beginning of trial
        """
        self.rect.y += 1/2*scaling
