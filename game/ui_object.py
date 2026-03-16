import pygame
from enum import Enum
from constants import GameConstants
from game_context import GameContext, GameState, LayerName
from game_object import GameObject
from utils import color_to_hex
import renpy
from frect import FRect
from renpy.display.render import render as renpy_render, Render
from renpy.display.imagelike import Solid



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
    def __init__(self, x, y, text, font, context, color=GameConstants.COLOR_UI_BASIC.value, size=20):
        self.text = text
        self.font = font
        self.color = color
        self.text_size = size
        super().__init__(x, y, None, context)
        self.num_frames = 1
        self.framerate = 1

        # Displayable de texto no estilo Ren'Py
        Text = renpy.store.Text
        self._text_displayable = Text(self.text, size = self.text_size, color = color_to_hex(self.color),)

        self.img = self._text_displayable
        w = self.context.w or GameConstants.WIDTH.value
        h = self.context.h or GameConstants.HEIGHT.value
        size_render = renpy_render(self.img, w, h, 0, 0)
        self.frame_width = size_render.width
        self.spritesheet_height = size_render.height
        self.update_body_from_image(x, y)

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

    def update_text_color(self, color):
        self.color = color
        Text = renpy.store.Text
        self._text_displayable = Text(self.text, size=self.text_size, color=color_to_hex(self.color))
        self.img = self._text_displayable
        renpy.exports.redraw(self, 0)

    def render(self, width, height, st, at):
        return super().render(width, height, st, at)


class UiOverlay(UiObject):
    """Overlay de fundo semi-transparente (ex.: para escurecer o fundo de um painel)."""
    def __init__(self, context, layer_name, color=(0, 0, 0, 128)):
        super().__init__(0, 0, "", context)
        self.layer_name = layer_name
        self._color = color
        self.body.width = GameConstants.WIDTH.value
        self.body.height = GameConstants.HEIGHT.value
        self.body.x = -context.screen.x

    def render(self, width, height, st, at):
        solid = Solid(self._color)
        r = Render(int(self.body.width), int(self.body.height))
        r.place(solid, 0, 0, int(self.body.width), int(self.body.height), st=st, at=at)
        return r


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

    def execute_render(self):
        my_render = super().execute_render()
        
        fill_width = self.value / (self.max_value - self.min_value) * self.body.width
        fill_frame = self.get_frame(0)

        original_width = self.body.width
        self.body.width = fill_width

        my_render = self.framed_render(fill_frame, my_render)
        self.body.width = original_width


class EffectDurationBar(UiObject):
    def __init__(self, effect, sprite_name, context):
        super().__init__(0, 0, sprite_name, context)
        self.effect = effect

        new_bar = UiBar(self.context, "bar_", pygame.Rect(0, 0, 64, self.body.height)) # will be positioned later
        new_bar.max_value = effect.duration
        new_bar.set_value(effect.duration)
        self.duration_bar = new_bar

    def current_frame_number(self):
        return 0 # always show first frame

    def reposition(self, x, y):
        self.body.x = x
        self.body.y = y
        self.duration_bar.body.x = self.body.x + self.body.width + 4
        self.duration_bar.body.y = self.body.y

    def execute_render(self):
        super().execute_render()
        duration_left = (self.effect.duration - self.effect.current_frame)
        duration_left = max(0, duration_left)
        self.duration_bar.set_value(duration_left)
        self.duration_bar.execute_render()