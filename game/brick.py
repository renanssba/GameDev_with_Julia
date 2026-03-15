import random

from game_object import GameObject
from sound_manager import SfxType
from powerup import Powerup, PowerupType
from constants import GameConstants


class Brick(GameObject):
    def __init__(self, x, y, hp, context):
        spritesheet_name = self.get_spritesheet_name(hp)
        # print("spritesheet_name: " + spritesheet_name)
        super().__init__(x, y, spritesheet_name, context)
        self.hp_max = hp
        self.hp = self.hp_max
        self.framerate = 0

    def get_spritesheet_name(self, hp):
        if hp > 5:
            name = "wall"
        else:
            name = "brick"
        # Randomly choose a letter from 'A' to 'D' to vary the brick type
        letter_appended = random.choice([chr(c) for c in range(ord('A'), ord('D')+1)])
        return name + letter_appended + "_"

    def apply_physics(self):
        pass

    def be_hit(self, damage=1):
        self.context.sound_manager.play_sfx(SfxType.BRICK_HIT)
        self.hp -= damage
        if self.hp <= 0:
            self.die()
            return

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
        fraction = float(self.hp) / float(self.hp_max)
        frame = int(fraction * (self.num_frames - 1))
        return (self.num_frames - 1 - frame)
