import pygame
from constants import GameConstants
from renpy.store import SfxType
from game_context import LayerName
from ui_panel import UiPanel
from ui_object import UiOption, UiLabel, UiOverlay, UiBar
import renpy


class OptionsContainer:
    def __init__(self, text, function):
        self.text = text
        self.function = function

class UiOptionsPanel(UiPanel):
    def __init__(self, context):
        options = [
            UiOption("Geral", self.toggle_master, context),
            UiOption("Som", self.toggle_sound, context),
            UiOption("Música", self.toggle_music, context),
            UiOption("Tela Cheia", self.toggle_fullscreen, context),
            UiOption("Voltar", self.close_panel, context),
        ]
        super().__init__("Opções", options, context)

        self.title.body.y -= 10

        # initialize values, load from file if exists
        self.option_values = [7, 7, 7, self.is_fullscreen(), '']
        self.option_values_labels = []
        self.load_options()
        for i, option in enumerate(self.options):
            option.ui_label.align_body_left()
            option.ui_label.body.x -= 30

            if i < 3:
                new_bar = UiBar(self.context, "bar_", pygame.Rect(option.ui_label.body.x, option.ui_label.body.y, 100, 16))
                new_bar.max_value = 1.0
                new_bar.set_value(self.option_values[i])
                new_bar.set_body_center(self.context.screen.width/2, option.ui_label.body_center().y)
                new_bar.align_body_right()
                self.option_values_labels.append(new_bar)
            else:
                new_label = UiLabel(0, 0, str(self.option_values[i]), self.context.ui_font_bold, self.context)
                new_label.set_body_center(self.context.screen.width/2, option.ui_label.body_center().y)
                new_label.align_body_right()
                new_label.update_text_color(GameConstants.COLOR_UI_BASIC.value)
                self.option_values_labels.append(new_label)
        self.update_labels()

        self.overlay = UiOverlay(context, LayerName.UI.value, GameConstants.COLOR_GAME_SPACE.value)

    # def show_panel(self):
    #     super().show_panel()
    #     # load values from preferences
    #     self.option_values[1] = self.sound_volume
    #     self.option_values[2] = self.music_volume
    #     print("SHOW PANEL: sound_volume:", self.sound_volume, "music_volume:", self.music_volume)
    #     self.update_volume_values()
    #     self.update_labels()

    def execute_render(self):
        super().execute_render()
        for i, option_value_label in enumerate(self.option_values_labels):
            option_value_label.execute_render()

    def process_panel_specific_inputs(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.confirm_input()
            elif event.key == pygame.K_LEFT:
                self.context.sound_manager.play_sfx(SfxType.UI_CONFIRM)
                if self.cursor < 3:
                    self.option_values[self.cursor] -= 0.05
                    self.update_volume_values()
                    self.update_labels()
                # elif self.cursor == 3:
                #     self.toggle_resolution_left()
                elif self.cursor == 3:
                    self.toggle_fullscreen()
        pass
    
    def toggle_master(self):
        self.option_values[0] += 0.05
        self.update_volume_values()
        self.update_labels()
    
    def toggle_sound(self):
        self.option_values[1] += 0.05
        self.update_volume_values()
        self.update_labels()
    
    def toggle_music(self):
        self.option_values[2] += 0.05
        self.update_volume_values()
        self.update_labels()

    def update_volume_values(self):
        self.option_values[0] = max(0, min(self.option_values[0], 1.0))
        self.option_values[1] = max(0, min(self.option_values[1], 1.0))
        self.option_values[2] = max(0, min(self.option_values[2], 1.0))
        self.context.sound_manager.set_volumes(self.option_values[0], self.option_values[1], self.option_values[2])

    def toggle_resolution_right(self):
        self.option_values[3] = (self.option_values[3] % 3) + 1
        self.update_labels()

    def toggle_resolution_left(self):
        self.option_values[3] = (self.option_values[3]+2) % 3
        if self.option_values[3] == 0:
            self.option_values[3] = 3
        self.update_labels()

    def is_fullscreen(self):
        return renpy.game.preferences.fullscreen
    
    def toggle_fullscreen(self):
        renpy.game.preferences.fullscreen = not renpy.game.preferences.fullscreen
        self.option_values[3] = self.is_fullscreen()
        self.update_labels()

    def update_labels(self):
        for i, option_value_label in enumerate(self.option_values_labels):
            if isinstance(option_value_label, UiLabel):
                option_value_label.update_text(str(self.option_values[i]))
            elif isinstance(option_value_label, UiBar):
                option_value_label.set_value(self.option_values[i])

    def cancel_input(self):
        super().cancel_input()
        self.close_panel()

    def close_panel(self):
        self.save_options()
        self.context.game_controller.close_current_panel()


    def save_options(self):
        pass

    def load_options(self):
        if not hasattr(renpy.game.persistent, "options") or renpy.game.persistent.options is None or len(renpy.game.persistent.options) == 0:
            return
        data = renpy.game.persistent.options

        self.option_values[0] = self.context.sound_manager.get_all_volumes()["main"]
        self.option_values[1] = self.context.sound_manager.get_all_volumes()["sfx"]
        self.option_values[2] = self.context.sound_manager.get_all_volumes()["music"]
        self.option_values[3] = self.is_fullscreen()

        # apply loaded values to the context
        self.context.sound_manager.set_volumes(self.option_values[0], self.option_values[1], self.option_values[2])