from enum import Enum
import random

import pygame

from game_object import GameObject
from sound_manager import SfxType
from vector2 import Vector2
from constants import GameConstants
from effects import EffectType


class PowerupType(Enum):
    SLOW_BALLS = "powerupA_"
    STICKY_PADDLE = "powerupB_"
    MULTIPLY_BALL = "powerupC_"
    ENLARGE_PADDLE = "powerupD_"
    SHOOTING_PADDLE = "powerupE_"

    HASTE_BALLS = "malusA_"
    SHRINK_PADDLE = "malusB_"

    HEART = "heartUI_"
    COIN = "coin_"
    RANDOM = "random"


class Powerup(GameObject):
    def __init__(self, context, x, y, powerup_type: PowerupType):
        if powerup_type == PowerupType.RANDOM:
            powerup_type = self.random_powerup_type(context)
        super().__init__(x, y, powerup_type.value, context)
        self.velocity = Vector2(0, 1.5)
        self.align_body_left()
        self.powerup_type = powerup_type

    def random_powerup_type(self, context):
        # drop specific powerups in debug mode
        if context.debug:
            return self.debug_specific_powerup()

        # Keep selecting until it's a valid powerup type
        while True:
            powerup_type = random.choice(list(PowerupType))
            if powerup_type != PowerupType.COIN and powerup_type != PowerupType.RANDOM:
                return powerup_type

    def debug_specific_powerup(self):
        debug_list = [
            PowerupType.SLOW_BALLS,
            PowerupType.HASTE_BALLS
            # PowerupType.SHOOTING_PADDLE
            # PowerupType.STICKY_PADDLE,
            ]
        return random.choice(debug_list) # DEBUG

    def apply_physics(self):
        super().apply_physics()
        if self.collide_with(self.context.player):
            self.be_collected()
            return

        if self.fell_from_screen():
            self.die()
            return

    def be_collected(self):
        # print("POWERUP COLLECTED: ", self.powerup_type)

        # play SFX
        if self.powerup_type == PowerupType.COIN:
            self.context.sound_manager.play_sfx(SfxType.COIN)
        elif self.powerup_type == PowerupType.SHRINK_PADDLE or self.powerup_type == PowerupType.HASTE_BALLS:
            self.context.sound_manager.play_sfx(SfxType.MALUS_GET)
        else:
            self.context.sound_manager.play_sfx(SfxType.POWERUP_GET)

        # spawn text particle
        if self.powerup_type != PowerupType.COIN:
            string = str(self.powerup_type)+"!"
            string = string.replace("_", " ")
            string = string.replace("PowerupType.", "")
            string = string.capitalize()
            self.spawn_text_particle(string, 14, 180)

        powerup_duration = GameConstants.POWERUP_DURATION.value
        malus_duration = GameConstants.MALUS_DURATION.value

        # collect powerup grants 20 points, coins grant 100
        if self.powerup_type == PowerupType.COIN:
            self.context.game_controller.gain_score(100, None)
        else:
            self.context.game_controller.gain_score(20, None)

        # execute powerup effect
        sprite_name = self.powerup_type.value
        match self.powerup_type:
            case PowerupType.COIN:
                pass # coins are already granted 100 points
            case PowerupType.HEART:
                if self.context.lives < GameConstants.MAX_LIVES.value:
                    self.context.lives += 1
                else:
                    self.context.game_controller.gain_score(200, None) # if max lives, grant more 200 points

            case PowerupType.ENLARGE_PADDLE:
                self.context.player.effect_controller.add_effect(EffectType.ENLARGE_PADDLE, 16, powerup_duration, sprite_name)
            case PowerupType.SHRINK_PADDLE:
                self.context.player.effect_controller.add_effect(EffectType.SHRINK_PADDLE, 16, malus_duration, sprite_name)
            
            case PowerupType.SHOOTING_PADDLE:
                self.context.player.effect_controller.add_effect(EffectType.SHOOTING_PADDLE, 16, powerup_duration/2, sprite_name)
            case PowerupType.STICKY_PADDLE:
                self.context.player.effect_controller.add_effect(EffectType.STICKY_PADDLE, 16, powerup_duration, sprite_name)

            case PowerupType.SLOW_BALLS:
                self.context.game_controller.effect_controller.add_effect(EffectType.SLOW_BALLS, 0.5, powerup_duration/2, sprite_name)
            case PowerupType.HASTE_BALLS:
                self.context.game_controller.effect_controller.add_effect(EffectType.HASTE_BALLS, 0.5, powerup_duration/2, sprite_name)
            
            case PowerupType.MULTIPLY_BALL:
                self.context.game_controller.multiply_ball()
        self.die()

    def die(self):
        self.context.game_objects.remove(self)
