from ui_panel import UiPanel
from game_context import GameState
from ui_options_panel import UiOption

class UiTransitionPanel(UiPanel):
    def __init__(self, transition_data, context):
        options = []

        for option in transition_data.options:
            options.append(UiOption(option.name, self.transition, context))
        super().__init__(transition_data.name, options, context)

    def transition(self):
        self.context.game_controller.set_game_state(GameState.RUNNING)
