import os
import renpy
import renpy.display.im as im
from renpy.display.render import Render
from renpy.display.render import render as renpy_render
from renpy.display.layout import Transform
from renpy.display.imagelike import Frame
from renpy.display.displayable import Displayable
import pygame
import re

from game_context import GameContext, LayerName
from vector2 import Vector2
from frect import FRect
from effects import EffectType
from effect_controller import EffectController


class GameObject(Displayable):
    """Base class for objects that have an image and position on the screen."""
    def __init__(self, x, y, img_name, context):
        Displayable.__init__(self)
        self.context = context

        # Timed effects like VFX and gameplay status effects
        self.effect_controller = EffectController(self)

        # Rendering
        self.layer_name = LayerName.FOREGROUND  # default layer for objects is foreground
        self.img = None
        self.frame_width = 0
        self.framerate = 4
        self.num_frames = 1
        self.render_condition = None
        
        if img_name != "" and img_name != None:
            self.img = self.load_spritesheet(img_name)
            self.num_frames = self.get_number_of_frames(img_name)
            self.spritesheet_width, self.spritesheet_height = self.get_sprite_size(self.img_path(img_name, ""))

            if self.img is not None:
                self.frame_width = self.spritesheet_width / self.num_frames

        self.scale = Vector2(1, 1)

        # Physics
        self.velocity = Vector2(0, 0)
        # Alinhamento (0.0–1.0): Default: usa body.x/body.y; 0.5 = centro
        self.self_xalign = 0.0
        self.self_yalign = 0.0
        self.update_body_from_image(x, y)
        

    ### SETUP AND INITIALIZATION ###
    def load_spritesheet(self, img_name):
        num_frames = self.get_number_of_frames(img_name)

        if img_name.endswith('_'):
            sprite_path = self.img_path(img_name, num_frames)
            if self.sprite_exists(sprite_path):
                self.img_skins = []
                self.img_skins.append(im.Image(sprite_path))
                self.img_skins.append(im.Image(self.img_path_reskin(img_name, num_frames)))
                return self.img_skins[self.context.reskin] # return correct skin
        
        sprite_path = self.img_path(img_name, "")
        if self.sprite_exists(sprite_path):
            self.img_skins = []
            self.img_skins.append(im.Image(sprite_path))
            self.img_skins.append(im.Image(self.img_path_reskin(img_name, "")))
            return self.img_skins[self.context.reskin] # return correct skin

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
    
    ### RESKIN SYSTEM ###
    def img_path_reskin(self, img_name, index):
        return f"sprites_reskin/{img_name}{index}.png"

    def update_skin(self):
        if hasattr(self, 'img_skins') and len(self.img_skins) > 0:
            self.img = self.img_skins[self.context.reskin]

    def sprite_exists(self, sprite_path):
        if renpy.loader.loadable(sprite_path):
            return True
        else:
            return False

    def get_sprite_size(self, sprite_path):
        if self.img is not None:
            return renpy.exports.image_size(self.img)
        else:
            return (0, 0)

    
    def update_body_from_image(self, x, y):
        if hasattr(self, 'img') and self.img is not None:
            self.body = FRect(x, y, self.frame_width, self.spritesheet_height)
        else:
            self.body = FRect(x, y, 0, 0)


    ### RENDERING ###
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
        if self.num_frames <= 1:
            return self.img
        x = int(frame_number * self.frame_width)
        w = int(self.frame_width)
        h = int(self.spritesheet_height)
        return im.Crop(self.img, (x, 0, w, h))

    def current_frame_number(self):
        # The object's current frame number based on the game current frame and the object's framerate
        if self.framerate == 0:
            return 0
        return int((self.context.current_frame / self.framerate) % self.num_frames)

    
    def execute_render(self):
        my_render = self.render(self.context.w, self.context.h, self.context.st, self.context.at)
        rw, rh = my_render.width, my_render.height
        
        renderX = int(self.body.x) - int((self.body.width) * self.self_xalign) + self.context.screen.x
        renderY = int(self.body.y) - int((self.body.height) * self.self_yalign) + self.context.screen.y
        
        my_layer = self.context.get_layer(self.layer_name)
        if my_layer is not None:
            my_layer.blit(my_render, (renderX, renderY))
        return my_render
        
    
    def render(self, width, height, st, at):
        if hasattr(self, 'render_condition') and self.render_condition is not None:
            if not self.render_condition():
                return Render(0, 0)

        frame = self.current_frame()
        if frame is None:
            return Render(0, 0)
        else:
            if self.body.width != self.frame_width:
                my_render = self.framed_render(frame)
            else:
                my_render = self.simple_render(frame)

        if self.context.debug:
            my_render = self.draw_bounding_box(my_render)

        return my_render

    def draw_bounding_box(self, prev_render):
        frame = self.context.debug_frame
        return self.framed_render(frame, prev_render)


    def simple_render(self, frame, my_render=None):
        obj_render = renpy_render(frame, self.context.w, self.context.h, self.context.st, self.context.at)
        if my_render is None:
            my_render = Render(self.body.width, self.body.height)
        my_render.blit(obj_render, (0, 0))
        return my_render

    def framed_render(self, frame, my_render=None):
        # Cria Render do tamanho do body. Frame renderiza as bordas depois preenche a área.
        border_w = self.frame_width/2-1
        border_h = self.spritesheet_height/2-1

        w = int(self.body.width)
        h = int(self.body.height)
        framed = Frame(frame, border_w, border_h, border_w, border_h)
        if my_render is None:
            my_render = Render(w, h)
        my_render.place(framed, 0, 0, w, h, st=self.context.st, at=self.context.at)
        return my_render

    def spawn_text_particle(self, text, size=8, duration=120):
        from particle import TextParticle
        text_particle = TextParticle(self.context, self.body_center().x, self.body_center().y, text, duration, size)
        self.context.game_objects.append(text_particle)


    ### PHYSICS AND BODY ###
    def apply_physics(self, time_scale=1.0):
        self.body.x += self.velocity.x * time_scale
        self.body.y += self.velocity.y * time_scale

        self.effect_controller.update()

        # apply linear drag to ball slowly decelerate
        if hasattr(self, 'linear_drag') and hasattr(self, 'desired_vel_lgth'):
            vel_length = self.velocity.length()
            desired_length = self.desired_vel_lgth
            if self.linear_drag != 0 and vel_length > desired_length:
                dragged_speed = max(desired_length, vel_length - self.linear_drag * time_scale)
                self.velocity.scale_to_length(dragged_speed)

    def collide_with(self, other):
        return self.body.colliderect(other.body)

    def limit_to_screen(self):
        did_clamp_x = False
        did_clamp_y = False
        clamped_x = max(0, min(self.body.x, self.context.screen.width - self.body.w))
        clamped_y = max(0, min(self.body.y, self.context.screen.height - self.body.h))
        if clamped_x != self.body.x:
            self.body.x = clamped_x
            did_clamp_x = True
        if clamped_y != self.body.y:
            self.body.y = clamped_y
            did_clamp_y = True
        return did_clamp_x or did_clamp_y

        # old implementation
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

    def set_align(self, xalign=None, yalign=None):
        """Posiciona o objeto por alinhamento (0.0=esq/topo, 0.5=centro, 1.0=dir/baixo). yalign opcional."""
        if xalign is not None:
            self.xalign = xalign
        if yalign is not None:
            self.yalign = yalign

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
