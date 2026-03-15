import pygame
import random
import math

from constants import GameConstants
from effects import EffectType
from ui_object import UiLabel
from game_object import GameObject
from trail_renderer import TrailRenderer
from sound_manager import SfxType
from brick import Brick
from particle import Particle, ParticleType
from object_spawner import ObjectSpawner
from vector2 import Vector2


class BallLevel:
    def __init__(self, sprite, trail_color, trail_size):
        self.sprite = sprite
        self.trail_color = trail_color
        self.trail_size = trail_size



class Ball(GameObject):
    def __init__(self, x, y, context):
        super().__init__(x, y, "ball", context)

        # x and y are the center of the ball
        self.set_body_center(x, y)

        # extra sprites
        self.img_default = self.img
        self.img_strong = self.load_spritesheet("ball_strong_")
        self.img_power = self.load_spritesheet("ball_power_")
        self.player_combo = 0 # number of times the ball has hit the player jumping
        self.num_frames = 1

        # ball levels (sprites and trail colors)
        level_0 = (BallLevel(self.img_default, (109, 138, 141, 255), GameConstants.BALL_DIAMETER.value-2))
        level_1 = (BallLevel(self.img_strong, (217, 36, 60, 128), GameConstants.BALL_DIAMETER.value))
        level_2 = (BallLevel(self.img_power, (255, 216, 50, 128), GameConstants.BALL_DIAMETER.value+6))
        self.ball_levels = [level_0, level_1, level_2]

        self.trail = TrailRenderer(context, max_positions=25, width=self.body.width-2, color=level_0.trail_color)
        self.stick_to_paddle()
        self.linear_drag = 0.0045
        self.velocity = Vector2(0, 0)

        # no particle generator by default
        self.particle_generator = None

        self.debug_label = UiLabel(0-self.context.screen.x, self.context.screen.height, "-\n-", self.context.ui_font, self.context)
        self.debug_label.align_body_top()
        self.debug_label.align_body_top()

    def be_launched(self):
        launch_velocity = Vector2(0, -3.5)
        launch_velocity += Vector2(0.0, -self.player_combo * 2.0)

        # Rotate the velocity by a random angle between 2 and 18 degrees. Avoid 0 to improve gameplay
        launch_velocity = launch_velocity.rotate(random.randint(2, 18))
        if random.random() < 0.5:
            launch_velocity.x = -launch_velocity.x

        self.stuck_to_paddle = False
        self.velocity = launch_velocity
        self.desired_vel_lgth = launch_velocity.length()

    def apply_physics(self):
        # generate particles if aplicable
        self.generate_particles()

        # If stuck to paddle, position in relation to it
        if self.stuck_to_paddle:
            self.velocity = Vector2(0, 0)
            pos_x = self.context.player.body_center().x + self.dist_to_paddle.x
            pos_y = self.context.player.body_center().y + self.dist_to_paddle.y
            self.set_body_center(pos_x, pos_y)
            # self.trail.clear()
            return
        
        # If not stuck to paddle, apply physics normally
        super().apply_physics(self.context.time_scale)
        
        # update trail positions
        # self.trail.update(self.body_center())

        # Bounce in walls
        if self.body.y < 0:
            self.context.sound_manager.play_sfx(SfxType.BALL_BOUNCE)
            self.bounce_y()
        if self.body.x + self.body.width > self.context.screen.width:
            self.context.sound_manager.play_sfx(SfxType.BALL_BOUNCE)
            self.bounce_x()
        if self.body.x < 0:
            self.context.sound_manager.play_sfx(SfxType.BALL_BOUNCE)
            self.bounce_x()

        # Hit paddle
        if self.collide_with(self.context.player) and self.velocity.y > 0:
            self.hit_paddle()
            return
        
        # Hit bricks
        for brick in self.context.game_objects:
            if isinstance(brick, Brick):
                if self.collide_with(brick):
                    if self.player_combo >= 2:
                        brick.be_hit(damage=100)
                    else:
                        brick.be_hit(damage=2)
                        normal = self.collision_normal(brick.body)
                        self.revert_before_collision(brick.body)
                        self.bounce_from_normal(normal)
                        return

        # Die if it falls off the screen
        if self.fell_from_screen():
            self.die()
        return


    ### COLISIONS AND COMBO ###
    def hit_paddle(self):
        player = self.context.player
        self.revert_before_collision(player.body)
        if player.velocity.y < 0:
            self.raise_combo()
            if self.player_combo >= 2:
                self.context.sound_manager.play_sfx(SfxType.BALL_BOUNCE_POWER)
                self.context.sound_manager.play_sfx(SfxType.FIRE)
                if self.player_combo == 2:
                    self.context.game_controller.effect_controller.add_effect(EffectType.HITSTOP, 5, 1)
            else:
                self.context.sound_manager.play_sfx(SfxType.BALL_HIT_PADDLE)
        else:
            self.context.sound_manager.play_sfx(SfxType.BALL_BOUNCE_PADDLE)
            # if self.player_combo < 2: #TODO: test if should never reset combo
            self.reset_combo()
        if self.context.player.is_sticky():
            self.stick_to_paddle()
        else:
            self.velocity = self.reflection_from_paddle(self.context.player)    

    def stick_to_paddle(self):
        self.reset_combo()
        self.stuck_to_paddle = True
        self.velocity = Vector2(0, 0)
        self.dist_to_paddle = self.body_center() - self.context.player.body_center()

    def raise_combo(self, amount=1):
        self.player_combo += amount
        self.update_sprite()
        if self.player_combo == 2:
            width = GameConstants.BALL_DIAMETER.value
            self.particle_generator = ObjectSpawner(self.context, Particle, 2, pygame.Rect(-width/2, -width/2, width, width))
            self.particle_generator.particle_type = ParticleType.FIRE
            self.particle_generator.parent = self
            self.particle_generator.objs_per_burst = 6

    def reset_combo(self):
        self.player_combo = 0
        self.update_sprite()
        self.particle_generator = None


    ### PHYSICS ###
    def bounce_x(self):
        self.limit_to_screen()
        self.velocity.x = -self.velocity.x
    
    def bounce_y(self):
        self.limit_to_screen()
        self.velocity.y = -self.velocity.y
    
    def bounce_from_normal(self, normal):
        self.velocity = self.velocity.reflect(normal)
    
    def revert_before_collision(self, body):
        Vx = self.velocity.x
        Vy = self.velocity.y
        
        ball_down = self.y_bottom()
        ball_up = self.y_top()
        ball_left = self.x_left()
        ball_right = self.x_right()
        
        body_down = body.y + body.height
        body_up = body.y
        body_left = body.x
        body_right = body.x + body.width

        hit_y_ball_up = ball_down - body_up # isso deve ser maior que 0
        hit_y_ball_down = body_down - ball_up # isso deve ser maior que 0
        hit_y = min(hit_y_ball_up, hit_y_ball_down)

        hit_x_ball_left = ball_right - body_left # isso deve ser maior que 0
        hit_x_ball_right = body_right - ball_left # isso deve ser maior que 0
        hit_x = min(hit_x_ball_left, hit_x_ball_right)
        
        if Vx != 0:
            revert_time_x = hit_x / abs(Vx)
        else:
            revert_time_x = float('inf')
        if Vy != 0:
            revert_time_y = hit_y / abs(Vy)
        else:
            revert_time_y = float('inf')
        revert_time = min(revert_time_x, revert_time_y)

        self.body.x -= Vx * revert_time
        self.body.y -= Vy * revert_time

    def reflection_from_paddle(self, paddle):
        distance = self.body_center().x - paddle.body_center().x
        if distance < -2 or distance > 2: # avoid reflecting simply up
            distance += 2
        dist_normalized = distance / (paddle.body.width / 2)
        dist_normalized = max(-1, min(1, dist_normalized))
        
        paddle_normal = Vector2(6*dist_normalized, -2)
        reflection_speed = paddle_normal.normalize() * self.velocity.length()
        reflection_speed.y += (paddle.velocity.y / 3.0)
        return reflection_speed


    ### RENDERING ###
    def generate_particles(self):
        if self.particle_generator is not None:
            self.particle_generator.update()

    def render(self, width, height, st, at):
        self.trail.render()
        result = super().render(width, height, st, at)
        if self.context.debug:
            vel_str = f"({self.velocity.x:.3f}, {self.velocity.y:.3f})"
            debug_text = f"Vel {vel_str}\nCombo {self.player_combo}"
            self.debug_label.update_text(debug_text)
            self.debug_label.execute_render()
        return result

    def update_sprite(self):
        current_level = self.ball_levels[min(self.player_combo, 2)]
        
        self.img = current_level.sprite
        self.num_frames = self.get_sprite_size("")[0] / self.frame_width
        self.trail.color = current_level.trail_color
        self.trail.width = current_level.trail_size


    ### EFFECTS ###
    def multiply_ball(self):
        for i in range(3):
            new_ball = Ball(self.body_center().x, self.body_center().y, self.context)
            new_ball.raise_combo(self.player_combo)
            new_ball.be_launched()
            new_ball.velocity.scale_to_length(self.velocity.length())
            self.context.game_objects.append(new_ball)


    ### DESTRUCTION ###
    def die(self):
        self.context.sound_manager.play_sfx(SfxType.BALL_MISS)
        self.context.game_objects.remove(self)
