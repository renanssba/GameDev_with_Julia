import pygame
from ui_panel import UiPanel
from game_context import GameState, LayerName
from ui_object import UiObject, UiLabel, UiOverlay
from constants import GameConstants
from renpy.store import SfxType
from effects import EffectType


class UiGameplayPanel(UiPanel):
    def __init__(self, context):
        super().__init__("", [], context)
        self.overlay = None
        
        img = None
        dx = 8
        self.score_label = UiLabel(-context.screen.x + dx, 26, "0", context.ui_font, context)
        self.lives_icons = []
        for i in range(GameConstants.MAX_LIVES.value):
            self.lives_icons.append(UiObject(-context.screen.x + i * 20 + dx, 2, "heart", context))
            self.objects_to_reskin.append(self.lives_icons[i])

        # Background
        # self.bg = UiOverlay(context, LayerName.UI, GameConstants.COLOR_GAME_SPACE.value)
        # self.bg.layer_name = LayerName.BACKGROUND

        # Effect Duration bars
        self.effect_bars = []

        # Debug Label
        self.debug_ui = UiLabel(context.screen.x+context.screen.width, 4, "Debug", context.ui_font, context)
        # self.debug_ui.render_condition = (lambda: context.debug)
        self.debug_ui.align_body_left()
        self.debug_ui.align_body_left()
        
        # FPS Label (atualizado a cada 0.5s)
        self.debug_fps_label = UiLabel(context.screen.x+context.screen.width, context.screen.height, "FPS: 00", context.ui_font, context)
        self._fps_update_accum = 0.0
        self._fps_update_interval = 0.5
        # self.debug_fps_label.render_condition = (lambda: context.debug)
        self.debug_fps_label.align_body_left()
        self.debug_fps_label.align_body_left()
        self.debug_fps_label.align_body_top()
        self.debug_fps_label.align_body_top()

        # other objects
        self.powerup_spawner = None
        # self.powerup_spawner = ObjectSpawner(game, Powerup, 40, pygame.Rect(0, 0, game.screen.width, 0))
        # self.powerup_spawner.powerup_type = PowerupType.RANDOM
        # self.context.game_objects.append(self.powerup_spawner)


    def show_panel(self):
        super().show_panel()
        # reset effect bars
        self.effect_bars = []

        # Border
        bg = UiObject(0, 0, "gameplay_border", self.context)
        bg.body.width = self.context.screen.width
        bg.body.height = self.context.screen.height
        bg.layer_name = LayerName.BACKGROUND
        self.context.game_objects.append(bg)


    def hide_panel(self):
        super().hide_panel()
        # delete all gameplay objects to stop gameplay
        self.context.game_objects = []

    def execute_render(self):
        # lives
        for i in range(self.context.lives):
            self.lives_icons[i].execute_render()
        
        # score
        self.score_label.execute_render()

        # effect duration bars
        for bar in self.effect_bars:
            bar.execute_render()
        
        # debug info
        if self.context.debug:
            self.debug_ui.execute_render()
            self._fps_update_accum += self.context.delta_time
            if self._fps_update_accum >= self._fps_update_interval:
                self._fps_update_accum = 0.0
                fps = 1.0 / self.context.delta_time if self.context.delta_time > 0 else 0
                self.debug_fps_label.update_text(f"FPS: {fps:.1f}")
            self.debug_fps_label.execute_render()

    def update_ui(self):
        self.score_label.update_text(str(self.context.score))
        self.execute_render()


    # effect duration bars
    def add_effect_bar(self, new_bar):
        self.effect_bars.append(new_bar)
        self.reposition_effect_bars()

    def remove_effect_bar(self, effect):
        for bar in self.effect_bars:
            if bar.effect == effect:
                self.effect_bars.remove(bar)
                self.reposition_effect_bars()
                return

    def reposition_effect_bars(self):
        for i in range(len(self.effect_bars)):
            bar = self.effect_bars[i]
            bar.reposition(4 - self.context.screen.x, self.context.screen.height - (bar.body.height + 4) * (i + 1) - 4)


    def process_panel_specific_inputs(self, event):
        # PROCESS ALL GAMEPLAY INPUTS HERE
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.context.debug:
            self.context.game_controller.close_all_panels()
            return
            

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.context.game_controller.set_game_state(GameState.PAUSED)
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.context.player.action_button_pressed()
            if event.key == pygame.K_F2:
                self.context.game_controller.set_game_state(GameState.VICTORY)
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.context.player.action_button_pressed()