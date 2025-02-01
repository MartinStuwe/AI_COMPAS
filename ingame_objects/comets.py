import pygame
import os
import random
import actr.rpc_interface
import asyncio
import json
from actr.socket_manager import comet_socket, move_socket


def start_async_loop():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

class Comet(pygame.sprite.Sprite):
    global_id_counter = 0

    def __init__(self, pos, size):
        super().__init__()
        self.image = pygame.image.load(os.path.join('assets/comets', 'comet_master.png')).convert_alpha()
        self.random_angle = random.choice([0, 90, 180, 270])
        self.image = pygame.transform.rotate(pygame.transform.scale(self.image, (size, size)), self.random_angle)
        self.rect = self.image.get_rect(topleft=pos)
        self.last_sent = pygame.time.get_ticks()  # Initialize last_sent properly
        self.update_freq = 1000  # Increase frequency if needed (ms)
        global global_id_counter
        self.id = Comet.global_id_counter + 1
        Comet.global_id_counter += 1

    def update(self, speed, scaling, horizontal_movement):
        self.rect.y -= int(1 * scaling * speed)
        self.rect.x += int(horizontal_movement * scaling * speed)
        current_time = pygame.time.get_ticks()

        # comment out to see if still lagging
        if current_time - self.last_sent > self.update_freq:
            self.update_visicon()
            self.last_sent = current_time

    def update_visicon(self):
        message = f"{{\"method\": \"evaluate\", \"params\":[\"add-visicon-features\", \"compas-model\", [\"screen-x\", {self.rect.x}, \"screen-y\", {self.rect.y}, \"comet-id\", {self.id}]], \"id\": 1}}"

        actr.rpc_interface.communicate_socket(sock=comet_socket, message=message)


    