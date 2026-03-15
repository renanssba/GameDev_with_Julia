from ui_info_panel import UiInfoPanel
from constants import GameConstants

class UiEndCardPanel(UiInfoPanel):
    def __init__(self, font, options_list, context):
        super().__init__(font, options_list, context)

    def close_panel(self):
        print ("Closing end card panel")

        leaderboard_panel = self.context.game_controller.leaderboard_panel
        score = self.context.score
        pos_in_leaboard = leaderboard_panel.position_to_add_entry(score)
        print(f"Calculated position in leaderboard: {pos_in_leaboard}")

        super().close_panel()
        if pos_in_leaboard < GameConstants.LEADERBOARD_MAX_ENTRIES.value:
            leaderboard_panel.add_entry("", score)
            leaderboard_panel.start_input_player_name(pos_in_leaboard)
        else:
            # print ("No space in leaderboard")
            pass