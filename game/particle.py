import pygame
from enum import Enum
from game_context import LayerName
from game_object import GameObject
from vector2 import Vector2
from constants import GameConstants
from ui_object import UiLabel

class ParticleType(Enum):
    FIRE = "part_fire_"
    LOVE = "part_love_"
    PETAL = "part_petal_"
    HIT = "part_hit_"
    TEXT = "none"

class Particle(GameObject):
    def __init__(self, context, x, y, particle_type: ParticleType, lifetime = 60):
        super().__init__(x, y, particle_type.value, context)
        self.velocity = Vector2(0, -1)
        self.lifetime = lifetime
        self.lifetime_current = 0
        self.layer_name = LayerName.EFFECTS_BACK
    
    def apply_physics(self):
        super().apply_physics()
        self.lifetime_current += 1
        if self.lifetime_current >= self.lifetime:
            self.die()
    
    def die(self):
        self.context.game_objects.remove(self)


class TextParticle(Particle):
    def __init__(self, context, x, y, text, lifetime = 60):
        super().__init__(context, x, y, ParticleType.TEXT, lifetime)
        self.text = text
        self.font = context.score_font

        self.velocity = Vector2(0, -0.3)

        self.color = GameConstants.COLOR_WHITE.value
        self.layer_name = LayerName.EFFECTS_FRONT
        
        # TODO: Implement text particle
        self.label = UiLabel(0, 0, text, self.font, context, self.color)
        self.img = self.label.img
        self.frame_width = self.spritesheet_width
        self.num_frames = 1
        self.update_body_from_image(x, y)
        self.set_body_center(x, y)