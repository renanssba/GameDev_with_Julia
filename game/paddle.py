from enum import Enum
from constants import GameConstants
from game_object import GameObject
from vector2 import Vector2
from sound_manager import SfxType
from ball import Ball
from shot import Shot
from effects import EffectType

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

        self.prepare_ball()


    ### RENDERING ###
    def update_sprite(self):
        if self.effect_controller.has_effect(EffectType.SHOOTING_PADDLE):
            self.img = self.img_shooter
        elif self.effect_controller.has_effect(EffectType.STICKY_PADDLE):
            self.img = self.img_sticky
        else:
            self.img = self.img_default


    def apply_effect(self, effect_type: EffectType):
        super().apply_effect(effect_type)
        self.update_sprite()

    def remove_effect(self, effect_type: EffectType):
        super().remove_effect(effect_type)
        self.update_sprite()


    ### PHYSICS ###
    def apply_physics(self):
        # print("applying physics to paddle.velocity: " + str(self.velocity) + ", frame(" + str(self.context.current_frame) + ")")
        self.define_movement()

        if not self.touching_ground():
            gravity_scale = 1.0
            if self.velocity.y < 0:
                gravity_scale = 1.5
            self.velocity += self.gravity * gravity_scale #* delta_time
        super().apply_physics()
        if self.limit_to_screen():
            self.velocity.x = 0
        if self.touching_ground():
            self.velocity.y = 0

        # UPDATE EFFECTS
        self.effect_controller.update()
        if self.effect_controller.has_effect_activating(EffectType.SHOOTING_PADDLE):
            self.spawn_shots()

            
    def define_movement(self):
        if not self.context.game_controller.is_running():
            return
        
        self.velocity.x = 0
        if self.context.left_pressed:
            self.velocity.x -= self.move_speed
        if self.context.right_pressed:
            self.velocity.x += self.move_speed

        # Mouse input
        if self.input_type == InputType.MOUSE:
            mouse_pos_x = self.context.raw_mouse_x - self.context.screen.x
            # raw mouse position less the screen offset
            dist_x = mouse_pos_x - self.body_center().x

            dist_x = max(-self.move_speed, min(dist_x, self.move_speed))
            self.velocity.x = dist_x

    def mouse_moved(self):
        # print("MOUSE MOVED!")
        self.input_type = InputType.MOUSE

    def keyboard_used(self):
        self.input_type = InputType.KEYBOARD


    ### CHECKS ###
    def touching_ground(self):
        return self.body.y >= self.max_y
    
    def is_sticky(self):
        return self.effect_controller.has_effect(EffectType.STICKY_PADDLE)


    ### BALL MANAGEMENT ###
    def ball_pos(self):
        pos_x = self.body_center().x
        pos_y = self.body_center().y - self.body.height / 2 - GameConstants.BALL_DIAMETER.value / 2
        return Vector2(pos_x, pos_y)

    def prepare_ball(self):
        ball = Ball(self.ball_pos().x, self.ball_pos().y, self.context)
        self.context.game_objects.append(ball)

    def has_ball(self):
        for obj in self.context.game_objects:
            if isinstance(obj, Ball):
                if obj.stuck_to_paddle:
                    return True
        return False


    
    ### ACTIONS ###
    def action_button_pressed(self):
        if not self.context.game_controller.is_running():
            return
        
        if self.has_ball():
            self.launch_ball()
        
        if self.touching_ground():
            self.jump()
    
    def launch_ball(self):
        if not self.has_ball():
            return

        self.context.sound_manager.play_sfx(SfxType.BALL_LAUNCH)

        for ball in self.context.game_objects:
            if isinstance(ball, Ball):
                if ball.stuck_to_paddle:
                    ball.be_launched()


    def jump(self):
        self.context.sound_manager.play_sfx(SfxType.JUMP)
        self.velocity += self.jump_force
    

    def spawn_shots(self):
        shot_dx = 8
        new_shot = Shot(self.body.x, self.body.y, self.context)
        new_shot.align_body_left()
        new_shot.body.x += shot_dx
        self.context.game_objects.append(new_shot)
        
        new_shot = Shot(self.body.x + self.body.width, self.body.y, self.context)
        new_shot.align_body_left()
        new_shot.body.x -= shot_dx
        self.context.game_objects.append(new_shot)
