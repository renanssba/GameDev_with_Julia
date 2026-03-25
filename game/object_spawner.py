import pygame
import random

from powerup import Powerup, PowerupType
from particle import Particle, ParticleType

class ObjectSpawner():
    """Creates a new object every X frames."""

    def __init__(self, context, object_to_spawn_class, spawn_interval, rect = pygame.Rect(0, 0, 0, 0)):
        """
        Args:
            context: GameContext with current_frame.
            object_to_spawn_class: Class of the object to be spawned.
            spawn_interval: Number of frames between each spawn.
            rect: Rectangle where the object will be spawned.
            parent: Parent object to spawn the object relative to.
        """
        self.context = context
        self.object_to_spawn_class = object_to_spawn_class
        self.spawn_interval = spawn_interval
        self.count = spawn_interval
        self.rect = rect
        self.parent = None
        self.objs_per_burst = 1

    def update(self):
        if self.object_to_spawn_class is None:
            return

        self.count += 1
        if self.count >= self.spawn_interval:
            self.count = 0
            for i in range(self.objs_per_burst):
                self.spawn_object()

    def spawn_object(self):
        pos_x = random.randint(self.rect.x, self.rect.x + self.rect.width)
        pos_y = random.randint(self.rect.y, self.rect.y + self.rect.height)
        if self.parent is not None:
            pos_x += self.parent.body_center().x
            pos_y += self.parent.body_center().y

        if self.object_to_spawn_class == Powerup:
            new_object = self.object_to_spawn_class(self.context, pos_x, pos_y, self.powerup_type)
        elif self.object_to_spawn_class == Particle:
            new_object = self.object_to_spawn_class(self.context, pos_x, pos_y, self.particle_type)
        # new_object.limit_to_screen()

        if hasattr(self, 'objs_speed'):
            new_object.velocity = self.objs_speed
        if hasattr(self, 'objs_lifetime'):
            new_object.lifetime = self.objs_lifetime
        self.context.game_objects.append(new_object)
