import pygame
import re
from enum import Enum
from constants import GameConstants
from game_context import GameContext, GameState, LayerName
from game_object import GameObject
from utils import color_to_hex
import renpy
from renpy.display.render import render as renpy_render



class UiOption:
    def __init__(self, text, function, context):
        self.text = text
        self.function = function
        
        self.ui_label = UiLabel(0, 0, text, context.ui_font_bold, context)
        self.ui_label.align_body_left()

class PanelType(Enum):
    GAMEPLAY = "gameplay"
    MENU = "menu"
    INFO = "info"
    PAUSE = "pause"
    VICTORY = "victory"
    DEFEAT = "defeat"


class UiObject(GameObject):
    def __init__(self, x, y, img_name, context):
        super().__init__(x, y, img_name, context)
        self.layer_name = LayerName.UI

    def apply_physics(self):
        pass


class UiLabel(UiObject):
    def __init__(self, x, y, text, font, context, color=GameConstants.COLOR_UI_BASIC.value, size=22):
        self.text = text
        self.font = font
        self.color = color
        self.text_size = size
        super().__init__(x, y, None, context)
        self.num_frames = 1
        self.framerate = 1

        print("UiLabel constructor called!")

        # Displayable de texto no estilo Ren'Py
        Text = renpy.store.Text
        self._text_displayable = Text(self.text, size = self.text_size, color = color_to_hex(self.color),)
        print("Text displayable created successfully!")

        self.img = self._text_displayable
        w = self.context.w or GameConstants.WIDTH.value
        h = self.context.h or GameConstants.HEIGHT.value
        size_render = renpy_render(self.img, w, h, 0, 0)
        self.frame_width = size_render.width
        self.spritesheet_height = size_render.height
        self.update_body_from_image(x, y)
        print("Body updated successfully!")

    def update_text(self, text):
        self.text = text
        self._text_displayable.set_text(text)
        w = self.context.w or GameConstants.WIDTH.value
        h = self.context.h or GameConstants.HEIGHT.value
        st = getattr(self.context, 'st', 0)
        at = getattr(self.context, 'at', 0)
        size_render = renpy_render(self._text_displayable, w, h, st, at)
        self.frame_width = size_render.width
        self.spritesheet_height = size_render.height
        self.update_body_from_image(self.body.x, self.body.y)

    def render(self, width, height, st, at):
        return super().render(width, height, st, at)


class UiBar(UiObject):
    def __init__(self, context, bar_sprite_name, rect):
        super().__init__(rect.x, rect.y, bar_sprite_name, context)
        self.context = context
        self.body.width = rect.width
        self.body.height = rect.height
        self.set_body_center(rect.x, rect.y)

        self.min_value = 0
        self.max_value = 100
        self.set_value(100)

    def set_value(self, value):
        self.value = value

    def current_frame_number(self):
        return 1

    def render(self):
        super().render()
        width = int(self.value / (self.max_value - self.min_value) * self.body.width-2)
        fill_rect = pygame.FRect(self.body.x + self.context.screen.x+1, self.body.y + self.context.screen.y, width, self.body.height)
        fill_frame = self.get_frame(0)
        self.blit_3_slice(fill_frame, fill_rect)

