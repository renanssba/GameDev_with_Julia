import pygame
from renpy.display.render import render as renpy_render
import renpy
from game_context import LayerName
from vector2 import Vector2


class TrailRenderer:
    def __init__(self, context, max_positions=10, width=8, color=(255, 255, 255, 128)):
        self.context = context
        self.max_positions = max_positions
        self.color = color
        self.width = width
        self.layer_name = LayerName.EFFECTS_BACK
        self.positions = []

    def update(self, position):
        self.positions.append(position)
        if len(self.positions) > self.max_positions:
            self.positions.pop(0)

    def lerp_color(self, c1, c2, t):
        n = min(len(c1), len(c2))
        return tuple(int(c1[j] + (c2[j] - c1[j]) * t) for j in range(n))

    def execute_render(self):
        self.render(self.context.w, self.context.h, self.context.st, self.context.at)

    def render(self, width, height, st, at):
        my_render = self.context.get_layer(self.layer_name.value)
        canvas = my_render.canvas()

        r, g, b = self.color[:3]
        white_color = (r, g, b, 255)
        for i in range(len(self.positions) - 1):
            t = (i + 1) / len(self.positions)
            line_width = max(1, int(self.width * t))
            line_color = self.lerp_color(white_color, self.color, t)

            start = self.positions[i] + Vector2(self.context.screen.x, self.context.screen.y)
            end = self.positions[i + 1] + Vector2(self.context.screen.x, self.context.screen.y)
            
            canvas.line(line_color, (int(start.x), int(start.y)), (int(end.x), int(end.y)), line_width)

    def clear(self):
        self.positions = []