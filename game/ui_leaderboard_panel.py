import pygame
import random
import os
import json
from constants import GameConstants
from renpy.store import SfxType
from game_context import LayerName
from ui_panel import UiPanel
from ui_object import UiOption, UiLabel, UiOverlay, UiBar
import renpy

class LeaderboardEntry:
    def __init__(self, name, score):
        self.name = name
        self.score = score

class UiLeaderboardPanel(UiPanel):
    def __init__(self, context):
        options = [
            UiOption("Voltar", self.close_panel, context),
        ]
        super().__init__("Placar", options, context)

        # position Back button and Title further from the center
        self.options[0].ui_label.body.y = self.context.screen.height - 30
        self.title.body.y = 10

        # load entries from file
        self.load_entries()

        # DEBUG: generate random entries
        # self.generate_random_entries(2) # used for Debug
        # self.save_entries()

        self.player_input = ""
        self.inputing_name = False
        self.inputing_name_position = 0

        self.update_all_labels()
        self.overlay = UiOverlay(context, LayerName.UI.value, GameConstants.COLOR_GAME_SPACE.value)
        
        self.debug_label = UiLabel(0-self.context.screen.x, self.context.screen.height, "F11 - Reset Leaderboard", self.context.ui_font, self.context)


    def generate_random_entries(self, num):
        # generate some random entries
        for i in range(num):
            self.add_entry(f"Player {i+random.randint(1, 1000)}", random.randint(0, 1000))


    def update_all_labels(self):
        # generate labels for each entry
        top_y = 56
        self.labels = []
        for i in range(len(self.entries)):
            position_x = self.context.screen.width / 2
            if i < 5:
                position_x = self.context.screen.width / 2 - 200
            else:
                position_x = self.context.screen.width / 2 # + 100

            entry = self.entries[i]
            newLabel = UiLabel(position_x, top_y + (i%5) * 34, f"{entry.name} - {entry.score}", self.context.ui_font, self.context)
            # newLabel.align_body_left()
            self.labels.append(newLabel)
        

    def execute_render(self):
        if self.inputing_name: # hide "Back" option when inputing name
            hidden_options = self.options
            self.options = []
            super().execute_render()
            self.options = hidden_options
        else:
            super().execute_render()

        for i, label in enumerate(self.labels):
            if i == self.inputing_name_position and self.inputing_name:
                label.update_text_color(self.get_current_selected_color())
            else:
                label.update_text_color(GameConstants.COLOR_UI_BASIC.value)
            label.execute_render()
        
        if self.context.debug:
            self.debug_label.execute_render()


    def confirm_input(self):
        if self.inputing_name:
            self.confirm_player_name()
        else:
            self.close_panel()
    
    def cancel_input(self):
        self.close_panel()


    ### PLAYER INPUT ###
    def start_input_player_name(self, position):
        # open a panel to input the player name
        self.player_input = ""
        self.inputing_name = True
        self.spacebar_confirms_input = False
        self.inputing_name_position = position
        self.context.game_controller.open_panel(self)


    def process_panel_specific_inputs(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11 and self.context.debug:
            self.reset_entries()

        if not self.inputing_name:
            return
        if event.type == pygame.KEYDOWN:
            # Add character if pressed key is letter (A–Z)
            if pygame.K_a <= event.key <= pygame.K_z:
                offset = event.key - pygame.K_a
                char = chr(ord("A") + offset)
                self.add_char(char)
            # Add character if pressed key is number (0–9)
            if pygame.K_0 <= event.key <= pygame.K_9:
                char = chr(ord("0") + event.key - pygame.K_0)
                self.add_char(char)
            # Add space
            if event.key == pygame.K_SPACE:
                self.add_char(" ")
            # Remove character
            elif event.key == pygame.K_BACKSPACE:
                self.remove_char()

    def add_char(self, char):
        self.context.sound_manager.play_sfx(SfxType.UI_SELECT)
        if len(self.player_input) >= GameConstants.LEADERBOARD_MAX_NAME_LENGTH.value:
            return
        self.player_input += char
        self.update_player_name_label()
    def remove_char(self):
        self.player_input = self.player_input[:-1]
        self.update_player_name_label()
    def update_player_name_label(self):
        entry = self.entries[self.inputing_name_position]
        entry.name = self.player_input
        self.labels[self.inputing_name_position].update_text(f"{entry.name} - {entry.score}")

    def confirm_player_name(self):
        if len(self.player_input) == 0:
            self.context.sound_manager.play_sfx(SfxType.UI_FORBIDDEN)
            return
        self.context.sound_manager.play_sfx(SfxType.UI_CONFIRM)
        self.inputing_name = False
        self.spacebar_confirms_input = True
        self.save_entries()

    ### ADD ENTRY ###
    def position_to_add_entry(self, score):
        for i in range(len(self.entries)):
            entry = self.entries[i]
            if entry.score < score:
                return i
        return len(self.entries)

    def add_entry(self, name, score):
        # position above entries with a score lower than the new one
        position = self.position_to_add_entry(score)
        self.entries.insert(position, LeaderboardEntry(name, score))

        # cap the number of entries to the maximum
        if len(self.entries) > GameConstants.LEADERBOARD_MAX_ENTRIES.value:
            self.entries.pop()
        self.save_entries()

        self.update_all_labels()

    ### SAVE AND LOAD ###
    def save_entries(self):
        # salva no persistent do Ren'Py (persistente entre sessões)
        data = [{"name": e.name, "score": e.score} for e in self.entries]
        renpy.game.persistent.leaderboard = data
        renpy.exports.save_persistent()

    def load_entries(self):
        self.entries = []

        # usa o persistent real do jogo (renpy.game.persistent), não o módulo
        if not hasattr(renpy.game.persistent, "leaderboard") or renpy.game.persistent.leaderboard is None or len(renpy.game.persistent.leaderboard) == 0:
            return

        data = renpy.game.persistent.leaderboard
        for item in data:
            name = item.get("name", "Player")
            score = item.get("score", 0)
            self.entries.append(LeaderboardEntry(name, score))

    def reset_entries(self):
        self.entries = []
        self.save_entries()
        self.update_all_labels()