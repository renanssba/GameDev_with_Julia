import os
import pygame
import renpy

from constants import GameConstants
from paddle import Paddle
from vector2 import Vector2
from brick import Brick
from renpy.store import SfxType
from effects import EffectType
from ui_dialog import UiDialog
from particle import Particle, ParticleType
from object_spawner import ObjectSpawner


class StageController():
    def __init__(self, context):
        self.context = context

    def reset_stage(self):
        self.context.game_objects = []  # reset game objects
        self.stage_id = self.context.current_stage

        self.context.lives = GameConstants.INITIAL_LIVES.value
        self.context.score = 0
        self.context.time = 0
        self.context.game_controller.update_ui()
        self.create_player()
        self.load_level(self.stage_id)

        # play gameplay music
        if self.context.reskin == 0:
            self.context.sound_manager.play_music(SfxType.GAMEPLAY_MUSIC)



        # petals spawner
        self.particle_spawner = ObjectSpawner(self.context, Particle, 20, pygame.Rect(0, 0, self.context.screen.width*2, 0))
        self.particle_spawner.objs_per_burst = 3
        self.particle_spawner.objs_speed = Vector2(-0.3, 1.0)
        self.particle_spawner.objs_lifetime = 1200
        self.particle_spawner.particle_type = ParticleType.PETAL
        self.context.game_controller.spawner = self.particle_spawner


        # story part 2 "cutscene"
        if self.context.story_part == 2:
            dialogs = [
                UiDialog(self.context, "simon", "Então, agora dá pra pular!", 2, 3),
                UiDialog(self.context, "julia", "Que legal!", 7, 3),
                UiDialog(self.context, "simon", "Basta apertar Barra de Espaço.", 12, 3),
                UiDialog(self.context, "julia", "E se eu rebater a bola várias vezes?", 17, 3),
                UiDialog(self.context, "simon", "Porque não tenta e descobre?", 22, 3)
            ]
            for dialog in dialogs:
                self.context.game_objects.append(dialog)

        # story part 3 "cutscene"
        if self.context.story_part == 3:
            if self.context.current_stage == 3:
                dialogs = [
                    UiDialog(self.context, "simon", "O que tem de novo nessa versão?", 1, 4),
                    UiDialog(self.context, "julia", "Deixa eu apertar isso aqui!", 5, 3),
                    UiDialog(self.context, "simon", "Que engraçado!", 10, 3),
                    UiDialog(self.context, "julia", "Ativar Modo Julia...", 13.5, 3),
                    UiDialog(self.context, "julia", "Agora!", 16.5, 3),
                    UiDialog(self.context, "simon", "Hahaha, isso é tão legal!", 22, 3),
                    UiDialog(self.context, "simon", "De onde você tirou essa música?", 28, 3),
                    UiDialog(self.context, "julia", "É de um anime que eu gosto!", 32, 3),
                    UiDialog(self.context, "simon", "Você é muito criativa!", 36, 3),
                    UiDialog(self.context, "julia", "Eu sou a melhor, não sou?", 40, 3),
                    UiDialog(self.context, "julia", "Agora tem que vencer a fase!", 45, 3),
                    UiDialog(self.context, "julia", "Quero que você veja o que tem depois!", 48, 3)
                ]
                for dialog in dialogs:
                    self.context.game_objects.append(dialog)

                time_to_music = 8
                time_to_drop = 8.5
                time_to_reskin = time_to_music + time_to_drop
                self.context.game_controller.effect_controller.add_effect(EffectType.PLAY_JULIA_MUSIC_ON_END, 0, time_to_music*60)
                self.context.game_controller.effect_controller.add_effect(EffectType.ACTIVATE_RESKIN_ON_END, 0, time_to_reskin*60)

        if self.context.current_stage == 4:
            dialogs = [
                UiDialog(self.context, "simon", "O que é isso aqui?", 1, 4),
                UiDialog(self.context, "julia", "É uma Naomi Invader, é claro!", 5, 3),
                UiDialog(self.context, "julia", "O chefão desse jogo!", 10, 3),
                UiDialog(self.context, "simon", "Hahaha, é claro!", 14, 3),
                UiDialog(self.context, "simon", "O que é isso que ela lança?", 18, 3),
                UiDialog(self.context, "julia", "Setinhas do Dance Dance Supreme.", 22, 3),
                UiDialog(self.context, "julia", "Pelo menos NESSE jogo eu detono ela!", 28, 3),
                UiDialog(self.context, "julia", "Vamo lá, acabar com ela!", 32, 3)
            ]
            for dialog in dialogs:
                self.context.game_objects.append(dialog)


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
                        newBrick = Brick(i * GameConstants.BRICK_WIDTH.value + dx.x, j * GameConstants.BRICK_HEIGHT.value + dx.y, 12, self.context)
                        self.context.game_objects.append(newBrick)
                    elif char == "b":
                        newBrick = Brick(i * GameConstants.BRICK_WIDTH.value + dx.x, j * GameConstants.BRICK_HEIGHT.value + dx.y, 20, self.context)
                        self.context.game_objects.append(newBrick)

                    if newBrick is not None:
                        newBrick.body.width = GameConstants.BRICK_WIDTH.value
                        newBrick.body.height = GameConstants.BRICK_HEIGHT.value
