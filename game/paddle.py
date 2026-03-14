import renpy
import renpy.display.im as im
from renpy.display.render import Render
from vector2 import Vector2
from game_object import GameObject
from enum import Enum
from sound_manager import SfxType

class InputType(Enum):
    MOUSE = "mouse"
    KEYBOARD = "keyboard"


class Paddle(GameObject):
    def __init__(self, x, y, context):
        super().__init__(x, y, "paddle_", context)
        self.body.width = 40 # Override the body width
        # self.body.height = 6 # Override the body height
        
        # x and y args are the center of the paddle
        self.set_body_center(x, y)
        self.move_speed = 5
        
        # Rendering
        self.framerate = 20

        # Extra sprites
        self.img_default = self.img
        self.img_sticky = self.load_spritesheet("paddle_sticky_")
        self.img_shooter = self.load_spritesheet("paddle_shooter_")
        
        # Jumping physics
        self.max_y = y
        self.gravity = Vector2(0, 0.25)
        self.jump_force = Vector2(0, -4)

        # Input type
        self.input_type = InputType.KEYBOARD

        # Add to game objects
        self.context.game_objects.append(self)
        self.context.player = self

        # self.prepare_ball()

        ## SIMPLE RENDER DEBUG
        self.image = im.Image("sprites/paddle_2.png")
        # metade esquerda do paddle: crop=(x, y, largura, altura) em fração 0–1
        self.image_left_half = renpy.display.motion.Transform(
            self.image, crop=(0, 0, 0.5, 1.0)
        )
        self.img_part = []
        self.img_paddle_left = renpy.display.motion.Transform(
            self.image, crop=(0, 0, 0.5, 1.0)
        )
        self.img_paddle_right = renpy.display.motion.Transform(
            self.image, crop=(0.5, 0, 0.5, 1.0)
        )


    ### INPUTS ###
    def process_inputs(self):
        if not self.context.game_controller.is_running():
            return
        
        self.velocity.x = 0
        if self.context.left_pressed:
            self.velocity.x -= self.move_speed
        if self.context.right_pressed:
            self.velocity.x += self.move_speed

        # Mouse input
        if self.input_type == InputType.MOUSE:
            mouse_pos_x = pygame.mouse.get_pos()[0] # Raw mouse posisition
            mouse_pos_x -= self.context.screen.x # Remove the screen offset
            dist_x = mouse_pos_x - self.body_center().x

            dist_x = max(-self.move_speed, min(dist_x, self.move_speed))
            self.velocity.x = dist_x

    def mouse_moved(self):
        # print("MOUSE MOVED!")
        self.input_type = InputType.MOUSE

    def keyboard_used(self):
        self.input_type = InputType.KEYBOARD

    


    def current_frame_number(self):
        if self.framerate == 0:
            return 0
        return int((self.context.current_frame / self.framerate) % self.num_frames)

    def get_frame(self, frame_number):
        if self.img is None:
            print("get_frame returning None")
            return None
        if frame_number < 0 or frame_number >= self.num_frames:
            print("get_frame returning None")
            return None
        
        if frame_number < self.num_frames / 2:
            return self.img_paddle_left
        else:
            return self.img_paddle_right
        # w = 1.0 / self.num_frames
        # x = frame_number * w
        # return renpy.display.motion.Transform(self.img, crop=(x, 0, w, 1.0))

    def current_frame(self):
        return self.image_left_half
        if not hasattr(self, 'img') or self.img is None:
            return None
        print("current frame: ", self.current_frame_number())
        return self.get_frame(self.current_frame_number())




    # tentar reimplementar isso aqui
    def render(self, w, h, st, at):
        paddle_render = renpy.render(self.image_left_half, w, h, st, at)
        # paddle_render = renpy.render(self.get_image(st), w, h, st, at)
        paddle_w, paddle_h = paddle_render.width, paddle_render.height
        self.context.main_render.blit(paddle_render, (self.body.x, self.body.y))


        # frame_disp = self.get_image(st)
        # if frame_disp is None:
        #     return Render(0, 0)
        # return renpy.render(frame_disp, w, h, st, at)

    ### PHYSICS ###
    def apply_physics(self, delta_time):
        print("paddle velocity: " + str(self.velocity.x) + ", " + str(self.velocity.y) + ", pos: " + str(self.body.x) + ", " + str(self.body.y))
        if not self.touching_ground():
            gravity_scale = 1.0
            if self.velocity.y < 0:
                gravity_scale = 1.5
            self.velocity += self.gravity * gravity_scale #* delta_time
        super().apply_physics(delta_time)
        if self.limit_to_screen():
            self.velocity.x = 0
        if self.touching_ground():
            self.velocity.y = 0


    ### CHECKS ###
    def touching_ground(self):
        return self.body.y >= self.max_y
    
    def is_sticky(self):
        return self.effect_controller.has_effect(EffectType.STICKY_PADDLE)

        
    ### ACTIONS ###
    def jump(self):
        self.context.sound_manager.play_sfx(SfxType.JUMP.value)
        self.velocity += self.jump_force
