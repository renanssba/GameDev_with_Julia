import renpy
import renpy.display.im as im
from renpy.display.render import render as renpy_render
from renpy.display.layout import Transform
from renpy.display.render import Render
from renpy.display.displayable import Displayable
import pygame
import re

from game_context import GameContext, LayerName
from vector2 import Vector2
from frect import FRect
from effects import EffectType
from effect_controller import EffectController

class GameObject(Displayable):
# class GameObject():
    """Base class for objects that have an image and position on the screen."""
    def __init__(self, x, y, img_name, context):
        Displayable.__init__(self)
        self.context = context

        print(f"GameObject init: {img_name}")

        # Timed effects like VFX and gameplay status effects
        self.effect_controller = EffectController(self)

        # Rendering
        self.layer_name = LayerName.FOREGROUND  # default layer for objects is foreground
        self.img = None
        self.img_width = 0
        self.img_height = 0
        self.frame_width = 0
        self.framerate = 4
        self.num_frames = 1
        self.render_condition = None
        
        if img_name != "" and img_name != None:
            self.img = self.load_spritesheet(img_name)
            self.num_frames = self.get_number_of_frames(img_name)
            self.spritesheet_width, self.spritesheet_height = self.get_sprite_size(self.img_path(img_name, ""))

            if self.img is not None:
                print(">> GAME_OBJECT INIT: IMG loaded is NOT None!")
                self.frame_width = self.spritesheet_width / self.num_frames
            else:
                print(">> GAME_OBJECT INIT: IMG loaded is None!")
            print("")

        self.scale = Vector2(1, 1)

        # Physics
        self.velocity = Vector2(0, 0)
        self.update_body_from_image(x, y)
        

    ### SETUP AND INITIALIZATION ###
    def load_spritesheet(self, img_name):
        print("")
        print(f"Loading spritesheet: {img_name}")

        num_frames = self.get_number_of_frames(img_name)

        if img_name.endswith('_'):
            sprite_path = self.img_path(img_name, num_frames)
            if self.sprite_exists(sprite_path):
                return im.Image(sprite_path)
        
        sprite_path = self.img_path(img_name, "")
        if self.sprite_exists(sprite_path):
            return im.Image(sprite_path)

        print(f"ERROR: Sprite not found: {sprite_path}")
        return None
    

    def get_number_of_frames(self, img_name):
        if img_name.endswith('_'):
            for i in range(1, 17):
                sprite_path = self.img_path(img_name, i)
                if self.sprite_exists(sprite_path):
                    return i
        return 1
    
    def img_path(self, img_name, index):
        return f"sprites/{img_name}{index}.png"


    def sprite_exists(self, sprite_path):
        if renpy.loader.loadable(sprite_path):
            print(f"sprite {sprite_path} exists!")
            return True
        else:
            print(f"sprite {sprite_path} does not exist!")
            return False

    def get_sprite_size(self, sprite_path):
        if self.sprite_exists(sprite_path):
            return im.Image(sprite_path).get_size()
        else:
            return (0, 0)

    
    def update_body_from_image(self, x, y):
        if hasattr(self, 'img') and self.img is not None:
            self.body = FRect(x, y, self.frame_width, self.spritesheet_height)
        else:
            self.body = FRect(x, y, 0, 0)


    ### RENDERING ###
    def execute_render(self):
        my_render = self.render(self.context.w, self.context.h, self.context.st, self.context.at)
        self.context.main_render.blit(my_render, (int(self.body.x), int(self.body.y)))
    

    def render(self, width, height, st, at):
        if hasattr(self, 'render_condition') and self.render_condition is not None:
            if not self.render_condition():
                return Render(0, 0)

        frame = self.current_frame()
        if frame is None:
            return Render(0, 0)

        obj_render = renpy_render(frame, width, height, st, at)
        r = Render(obj_render.width, obj_render.height)
        r.blit(obj_render, (0, 0))
        return r

    def visit(self):
        if self.img is not None and callable(getattr(self.img, "render", None)):
            return [self.img]
        return []

    def current_frame(self):
        if not hasattr(self, 'img') or self.img is None:
            return None
        return self.get_frame(self.current_frame_number())

    def get_frame(self, frame_number):
        if not hasattr(self, 'img') or self.img is None:
            return None
        return self.img
        # TODO: reimplement the subsurface logic
        return self.img.subsurface(frame_number * self.frame_width, 0, self.frame_width, self.spritesheet_height)

    def current_frame_number(self):
        # The object's current frame number based on the game current frame and the object's framerate
        if self.framerate == 0:
            return 0
        return int((self.context.current_frame / self.framerate) % self.num_frames)

    def render_obj(self):
        if hasattr(self, 'render_condition') and self.render_condition is not None:
            if not self.render_condition():
                return

        blit_rect = FRect(self.body.x, self.body.y, self.body.width, self.body.height)
        blit_rect.x += self.context.screen.x
        blit_rect.y += self.context.screen.y

        frame = self.current_frame()
        if frame is not None:
            if self.body.width != frame.get_width():
                self.blit_3_slice(frame, blit_rect)
            else:
                self.blit_to_layer(frame, blit_rect)

        if self.context.debug:
            blit_rect.width = self.body.width
            pygame.draw.rect(self.context.get_layer(self.layer_name), (255, 0, 0), blit_rect, 1)

    def blit_to_layer(self, frame, blit_rect):
        self.context.get_layer(self.layer_name).blit(frame, blit_rect)

    def blit_3_slice(self, frame, blit_rect):
        frame_w = frame.get_width()
        frame_h = frame.get_height()
        slice_size = int(frame_w / 2 - 1)
        layer = self.context.get_layer(self.layer_name)

        # Left piece
        left_src = pygame.Rect(0, 0, slice_size, frame_h)
        left_dest = FRect(blit_rect.x, blit_rect.y, slice_size, blit_rect.height)
        layer.blit(frame, left_dest, area=left_src)

        # Right piece
        right_src = pygame.Rect(frame_w - slice_size, 0, slice_size, frame_h)
        right_dest = FRect(blit_rect.x + blit_rect.width - slice_size, blit_rect.y, slice_size, blit_rect.height)
        layer.blit(frame, right_dest, area=right_src)

        # Center piece (stretched to fill)
        center_src_w = frame_w - 2 * slice_size
        center_dest_w = blit_rect.width - 2 * slice_size
        if center_src_w > 0 and center_dest_w > 0:
            center_src = frame.subsurface(pygame.Rect(slice_size, 0, center_src_w, frame_h))
            center_scaled = pygame.transform.scale(center_src, (int(center_dest_w), int(blit_rect.height)))
            layer.blit(center_scaled, (blit_rect.x + slice_size, blit_rect.y))

    def spawn_text_particle(self, text):
        from particle import TextParticle
        text_particle = TextParticle(self.context, self.body_center().x, self.body_center().y, text, 120)
        self.context.game_objects.append(text_particle)


    ### INPUTS STUB ###
    def process_inputs(self):
        pass


    ### PHYSICS AND BODY ###
    def apply_physics(self, delta_time = 1.0):
        self.body.x += self.velocity.x * float(delta_time) * 60.0
        self.body.y += self.velocity.y * float(delta_time) * 60.0

        self.effect_controller.update()

        # apply linear drag to ball slowly decelerate
        if hasattr(self, 'linear_drag') and hasattr(self, 'desired_vel_lgth'):
            vel_length = self.velocity.length()
            desired_length = self.desired_vel_lgth
            if self.linear_drag != 0 and vel_length > desired_length:
                dragged_speed = max(desired_length, vel_length - self.linear_drag * delta_time)
                self.velocity.scale_to_length(dragged_speed)

    def collide_with(self, other):
        return self.body.colliderect(other.body)

    def limit_to_screen(self):
        half_width = self.body.width / 2
        clamped_x = max(half_width, min(self.body_center().x, self.context.screen.width - half_width))
        if clamped_x != self.body_center().x:
            self.set_body_center(clamped_x, self.body_center().y)
            return True
        return False

    def fell_from_screen(self):
        return self.body.y > self.context.screen.height

    def left_screen_up(self):
        return self.body.y - self.body.height < 0

    def collision_normal(self, other):
        """Returns the collision normal (pointing outward from the 'other' object)"""
        # Distances to the edges (penetrations in each direction)
        left = (self.body.right - other.left)
        right = (other.right - self.body.left)
        top = (self.body.bottom - other.top)
        bottom = (other.bottom - self.body.top)
        
        # Menor penetração = eixo da colisão
        min_overlap = min(left, right, top, bottom)
        
        if min_overlap == left:
            return Vector2(-1, 0)
        elif min_overlap == right:
            return Vector2(1, 0)
        elif min_overlap == top:
            return Vector2(0, -1)
        else:  # bottom
            return Vector2(0, 1)

    
    def increase_size(self, dx, dy):
        from paddle import Paddle
        cx = self.body_center().x
        cy = self.body_center().y

        self.body.width += dx
        self.body.height += dy
        self.set_body_center(cx, cy)

        if isinstance(self, Paddle):
            self.limit_to_screen()
    
    def body_center(self):
        return Vector2(self.body.x + self.body.width / 2, self.body.y + self.body.height / 2)

    def y_bottom(self):
        return self.body.y + self.body.height
    def y_top(self):
        return self.body.y
    def x_left(self):
        return self.body.x
    def x_right(self):
        return self.body.x + self.body.width

    def set_body_center(self, x, y):
        self.body.x = x - self.body.width / 2
        self.body.y = y - self.body.height / 2

    def align_body_left(self):
        self.body.x -= self.body.width / 2

    def align_body_right(self):
        self.body.x += self.body.width / 2

    def align_body_top(self):
        self.body.y -= self.body.height / 2

    def align_body_bottom(self):
        self.body.y += self.body.height / 2


    ### VISUAL AND STATUS EFFECTS ###
    def apply_effect(self, effect_type):
        match effect_type:
            case EffectType.ENLARGE_PADDLE:
                self.increase_size(32, 0)
            case EffectType.SHRINK_PADDLE:
                self.increase_size(-16, 0)

    def remove_effect(self, effect_type):
        match effect_type:
            case EffectType.ENLARGE_PADDLE:
                self.increase_size(-32, 0)
            case EffectType.SHRINK_PADDLE:
                self.increase_size(16, 0)


    ### DESTRUCTION ###
    def die(self):
        if self in self.context.game_objects:
            self.context.game_objects.remove(self)
        self.effect_controller.clear()
