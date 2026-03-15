import pygame

from game_object import GameObject
from brick import Brick
from vector2 import Vector2

class Shot(GameObject):
    def __init__(self, x, y, context):
        super().__init__(x, y, "shot_", context)
        self.body.width -= 4
        self.velocity = Vector2(0, -3)
        self.align_body_left()

    def apply_physics(self):
        # from brick import Brick
        super().apply_physics()

        # Hit bricks
        for brick in self.context.game_objects:
            if isinstance(brick, Brick):
                if self.collide_with(brick):
                    brick.be_hit(damage=1)
                    self.die()
                    return

        # Die if it leaves the screen
        if self.left_screen_up():
            self.die()

    # def die(self):
    #     print("shot died!!")
    #     self.context.game_objects.remove(self)