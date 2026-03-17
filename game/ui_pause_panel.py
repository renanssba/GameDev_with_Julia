import pygame

from ui_object import UiLabel, UiOverlay, UiOption
from ui_panel import UiPanel
from renpy.store import SfxType
from game_context import GameState


class UiPausePanel(UiPanel):
    def __init__(self, context):
        options_list = [
            UiOption("Continuar", self.continue_game, context),
            # UiOption("Restart", self.restart_game, context),
            UiOption("Opções", self.show_options, context),
            UiOption("Sair", self.quit_game, context),
        ]
        super().__init__("Paused", options_list, context)


    def show_panel(self):
        super().show_panel()
        self.context.sound_manager.play_sfx(SfxType.UI_PAUSE)

    def hide_panel(self):
        super().hide_panel()
        self.context.sound_manager.play_sfx(SfxType.UI_UNPAUSE)


    def render(self):
        self.overlay.render()
        super().render()
    
    def process_panel_specific_inputs(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.context.game_controller.close_current_panel()

    def continue_game(self):
        self.context.game_controller.close_current_panel()

    def restart_game(self):
        self.context.game_controller.close_current_panel()
        self.context.game_controller.stage_controller.reset_stage()

    def show_options(self):
        self.context.game_controller.set_game_state(GameState.OPTIONS)
        
    def quit_game(self):
        if self.context.arcade_mode:
            self.context.game_controller.set_game_state(GameState.TITLE)
        else:
            self.context.game_controller.close_all_panels()
