from game_object import GameObject
from vector2 import Vector2
from object_spawner import ObjectSpawner
from powerup import Powerup, PowerupType
from brick import Brick
from frect import FRect
import pygame

class Boss(Brick):
    def __init__(self, x, y, context):
        super().__init__(x, y, 20, context)

        self.img_name = "naomi_invader_"
        self.img = self.load_spritesheet(self.img_name)
        self.spritesheet_width, self.spritesheet_height = self.get_sprite_size("")
        self.frame_width = 80

        self.body = FRect(x, y, 80, 64)
        self.num_frames = 2
        self.framerate = 16
        self.velocity = Vector2(0.5, 0)
        
        self.powerup_spawner = ObjectSpawner(
            self.context,
            Powerup,
            130,
            pygame.Rect(self.body.x, self.body.y+self.body.height, self.body.width, 1),
        )
        self.powerup_spawner.powerup_type = PowerupType.STUN


    def apply_physics(self):
        GameObject.apply_physics(self)
        if self.body.x + self.body.width > self.context.screen.width:
            self.bounce_x()
        if self.body.x < 0:
            self.bounce_x()
        if self.powerup_spawner is not None:
            self.powerup_spawner.rect = pygame.Rect(self.body.x, self.body.y+self.body.height/2, self.body.width, 1)
            self.powerup_spawner.update()

    def bounce_x(self):
        self.limit_to_screen()
        self.velocity.x = -self.velocity.x

    def drop_item(self):
        pass
    
    def current_frame_number(self):
        return GameObject.current_frame_number(self)
