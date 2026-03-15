import os
import pygame
import renpy

from constants import GameConstants
from paddle import Paddle
from vector2 import Vector2
from brick import Brick


class StageController():
    def __init__(self, context):
        self.context = context

    def setup(self, stage_id):
        self.stage_id = stage_id
        self.reset_stage()

    def reset_stage(self):
        self.context.game_objects = []  # reset game objects
        self.context.stage_id = self.stage_id

        self.context.lives = GameConstants.INITIAL_LIVES.value
        self.context.score = 0
        self.context.time = 0
        self.context.game_controller.update_ui()
        self.create_player()
        self.load_level(self.stage_id)

    def create_player(self):
        player_x = self.context.screen.width / 2
        player_y = self.context.screen.height - 30
        self.context.game_controller.paddle = Paddle(player_x, player_y, self.context)

    def load_level(self, stage_id):
        filename = "stages/stage" + str(stage_id) + ".txt"
        with renpy.exports.open_file(filename, encoding="utf-8") as file:
            for j, line in enumerate(file):
                dx = Vector2(0, 0)
                for i, char in enumerate(line):
                    newBrick = None
                    if char == " ":
                        continue
                    elif char == ">":
                        dx.x += GameConstants.BRICK_WIDTH.value / 2
                    elif char == "<":
                        dx.x -= GameConstants.BRICK_WIDTH.value / 2
                    elif char == "^":
                        dx.y += GameConstants.BRICK_HEIGHT.value / 2
                    elif char == "v":
                        dx.y -= GameConstants.BRICK_HEIGHT.value / 2
                    elif char == "-":
                        newBrick = Brick(i * GameConstants.BRICK_WIDTH.value + dx.x, j * GameConstants.BRICK_HEIGHT.value + dx.y, 4, self.context)
                        self.context.game_objects.append(newBrick)
                    elif char == "#":
                        newBrick = Brick(i * GameConstants.BRICK_WIDTH.value + dx.x, j * GameConstants.BRICK_HEIGHT.value + dx.y, 16, self.context)
                        self.context.game_objects.append(newBrick)

                    if newBrick is not None:
                        newBrick.body.width = GameConstants.BRICK_WIDTH.value
                        newBrick.body.height = GameConstants.BRICK_HEIGHT.value
