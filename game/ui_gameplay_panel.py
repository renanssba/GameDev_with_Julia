import pygame
from ui_panel import UiPanel
from game_context import GameState
from ui_object import UiObject, UiLabel
from constants import GameConstants
from sound_manager import SfxType


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

        # Debug Label
        self.debug_ui = UiLabel(context.screen.x+context.screen.width, 4, "Debug", context.ui_font, context)
        self.debug_ui.render_condition = (lambda: context.debug)
        self.debug_ui.align_body_left()
        self.debug_ui.align_body_left()
        context.game_objects.append(self.debug_ui)

        # other objects
        self.powerup_spawner = None
        # self.powerup_spawner = ObjectSpawner(game, Powerup, 40, pygame.Rect(0, 0, game.screen.width, 0))
        # self.powerup_spawner.powerup_type = PowerupType.RANDOM
        # self.context.game_objects.append(self.powerup_spawner)


    def show_panel(self):
        super().show_panel()
        self.context.sound_manager.play_music(SfxType.GAMEPLAY_MUSIC)

    def execute_render(self):
        for i in range(self.context.lives):
            self.lives_icons[i].execute_render()
        self.score_label.execute_render()

    def update_ui(self):
        self.score_label.update_text(str(self.context.score))
        self.execute_render()


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