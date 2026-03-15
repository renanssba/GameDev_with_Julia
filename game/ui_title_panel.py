import pygame

from ui_panel import UiPanel
from game_context import GameState, GameConstants, LayerName
from ui_object import UiOption, UiOverlay
from sound_manager import SfxType

class UiTitlePanel(UiPanel):
    def __init__(self, context):
        options = [
            UiOption("Play", self.start_game, context),
            UiOption("Leaderboards", self.show_leaderboard, context),
            UiOption("Options", self.show_options, context),
            UiOption("Exit", self.quit_game, context),
        ]
        super().__init__("BREAK OUT", options, context)
        self.overlay = UiOverlay(context, LayerName.UI.value, GameConstants.COLOR_GAME_SPACE.value)

    def show_panel(self):
        self.context.sound_manager.play_music(SfxType.MENU_MUSIC)
    
    def render(self):
        self.overlay.render()
        super().render()

    def start_game(self):
        self.context.game_controller.set_game_state(GameState.RUNNING)

    def show_leaderboard(self):
        self.context.game_controller.set_game_state(GameState.LEADERBOARD)

    def show_options(self):
        self.context.game_controller.set_game_state(GameState.OPTIONS)

    def quit_game(self):
        self.context.game_controller.close_all_panels()