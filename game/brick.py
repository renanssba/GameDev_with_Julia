import random
import pygame

from game_object import GameObject
from sound_manager import SfxType
from powerup import Powerup, PowerupType
from constants import GameConstants
from particle import ParticleType, Particle
from vector2 import Vector2
from object_spawner import ObjectSpawner


class Brick(GameObject):
    def __init__(self, x, y, hp, context):
        spritesheet_name = self.get_spritesheet_name(hp)
        print("spritesheet_name: " + spritesheet_name)
        super().__init__(x, y, spritesheet_name, context)
        self.hp_max = hp
        self.hp = self.hp_max
        self.framerate = 0
        
        self.powerup_spawner = None

        # Special settings for Naomi boss
        if spritesheet_name == "face_naomi":
            print("sprite name: " + spritesheet_name + ", setting body width and height to 64")
            self.body.w = 64
            self.body.h = 64
            self.frame_width = 64
            self.spritesheet_height = 64
            self.spritesheet_width = 64

            self.powerup_spawner = ObjectSpawner(
                self.context,
                Powerup,
                90,
                pygame.Rect(0, 0, self.context.screen.width, 2),
            )
            self.powerup_spawner.powerup_type = PowerupType.STUN


    def get_spritesheet_name(self, hp):
        if hp >= 20:
            return "face_naomi"
        elif hp > 5:
            name = "wall"
        else:
            name = "brick"
        # Randomly choose a letter from 'A' to 'D' to vary the brick type
        letter_appended = random.choice([chr(c) for c in range(ord('A'), ord('D')+1)])
        return name + letter_appended + "_"

    def apply_physics(self):
        if self.powerup_spawner is not None:
            self.powerup_spawner.update()
        pass

    def be_hit(self, damage=1, shot_body=None):
        self.context.sound_manager.play_sfx(SfxType.BRICK_HIT)
        if shot_body is not None and self.context.advanced_features:
            self.spawn_hit_particle(shot_body)
        self.hp -= damage
        if self.hp <= 0:
            self.die()
            return

    def spawn_hit_particle(self, shot_body):
        hit_particle = Particle(self.context, 0, 0, ParticleType.HIT)
        hit_particle.velocity = Vector2(0, 0)

        part_frames = hit_particle.num_frames
        part_framerate = hit_particle.framerate
        hit_particle.lifetime = part_frames * part_framerate
        hit_particle.set_body_center(shot_body.center[0], shot_body.center[1])
        self.context.game_objects.append(hit_particle)


    def die(self):
        self.context.game_controller.gain_score(100, self)
        self.context.game_objects.remove(self)
        self.drop_item()
        

    def drop_item(self):
        random_selection = random.random()
        coin_range = self.context.brick_coin_chance
        powerup_range = self.context.brick_powerup_chance + coin_range

        if random_selection < coin_range:
            powerup = Powerup(self.context, self.body_center().x, self.body_center().y, PowerupType.COIN)
            self.context.game_objects.append(powerup)
        elif random_selection < powerup_range:
            powerup = Powerup(self.context, self.body_center().x, self.body_center().y, PowerupType.RANDOM)
            self.context.game_objects.append(powerup)


    def current_frame_number(self):
        if self.hp_max >= 20:
            return 0
        fraction = float(self.hp) / float(self.hp_max)
        frame = int(fraction * (self.num_frames - 1))
        return (self.num_frames - 1 - frame)
