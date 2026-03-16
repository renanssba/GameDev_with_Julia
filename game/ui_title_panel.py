import pygame

from ui_panel import UiPanel
from game_context import GameState, GameConstants, LayerName
from ui_object import UiOption, UiOverlay, UiObject
from sound_manager import SfxType

class UiTitlePanel(UiPanel):
    def __init__(self, context):
        options = [
            UiOption("Play", self.start_game, context),
            UiOption("Leaderboards", self.show_leaderboard, context),
            UiOption("Options", self.show_options, context),
            UiOption("Exit", self.quit_game, context),
        ]
        super().__init__("", options, context)
        self.overlay = UiOverlay(context, LayerName.UI.value, GameConstants.COLOR_GAME_SPACE.value)

        self.offset_options_labels(0, 20)

        self.logo = UiObject(-self.context.screen.x, -self.context.screen.y, "logo", context)
        self.objects_to_reskin.append(self.logo)

    def show_panel(self):
        self.context.sound_manager.play_music(SfxType.MENU_MUSIC)
    
    def execute_render(self):
        self.overlay.execute_render()
        super().execute_render()
        self.logo.execute_render()

    def start_game(self):
        self.context.current_stage = self.context.start_stage
        self.context.game_controller.set_game_state(GameState.RUNNING)

    def show_leaderboard(self):
        self.context.game_controller.set_game_state(GameState.LEADERBOARD)

    def show_options(self):
        self.context.game_controller.set_game_state(GameState.OPTIONS)

    def quit_game(self):
        self.context.game_controller.close_all_panels()