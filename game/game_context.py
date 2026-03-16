import pygame
import renpy.display.im as im
from enum import Enum
from constants import GameConstants

class GameState(Enum):
    RUNNING = "running"
    PAUSED = "paused"
    VICTORY = "victory"
    DEFEAT = "defeat"
    TITLE = "title"
    LEADERBOARD = "leaderboard"
    OPTIONS = "options"
    TRANSITION = "transition"

class LayerName(Enum):
    BACKGROUND = "background"
    EFFECTS_BACK = "effects_back"
    FOREGROUND = "foreground"
    EFFECTS_FRONT = "effects_front"
    UI = "ui"


class GameContext:
    def __init__(self, width, height, game_space_width, game_space_height, story_part):
        # Guardar resolução base para permitir trocar escala depois
        self._base_width = width
        self._base_height = height
        
        # Current Stage
        self.load_config(story_part)
        self.current_stage = self.start_stage

        # DEBUG: force current stage to fixed value
        self.current_stage = 1

        # Game space é a área onde os objetos são renderizados
        # x e y são a posição da "câmera"
        self._game_space = pygame.Rect(
            (width - game_space_width) / 2,
            (height - game_space_height) / 2,
            game_space_width,
            game_space_height,
        )

        # Game States
        self._clock = pygame.time.Clock()
        self.time_scale = 1.0
        self.debug = False
        self._state = GameState.RUNNING
        self._current_frame = 0
        self._unscaled_frame = 0

        # Input States (Ren'Py info)
        self.right_pressed = False
        self.left_pressed = False
        self.main_render = None
        self.w = 0
        self.h = 0
        self.st = 0
        self.at = 0
        self.delta_time = 0.0
        self.raw_mouse_x = 0
        self.raw_mouse_y = 0

        # Objects
        self.game_objects = []
        self.player = None
        self.sound_manager = None
        self.brick_coin_chance = GameConstants.BRICK_COIN_CHANCE.value
        self.brick_powerup_chance = GameConstants.BRICK_POWERUP_CHANCE.value

        # Surface layers
        self._background_layer = None
        self._effects_back_layer = None
        self._foreground_layer = None
        self._effects_front_layer = None
        self._ui_layer = None

        # Initialize fonts // TODO: Use Ren'Py fonts
        self.ui_font_bold = None
        self.ui_font = None
        self.score_font = None

        # Debug img
        self.debug_frame = im.Image("sprites/debug.png")

        # Score and Lives
        self.score = 0
        self.lives = GameConstants.INITIAL_LIVES.value

        # Game Controller
        self.game_controller = None

    def load_config(self, story_part):
        self.advanced_features = True
        self.arcade_mode = False
        self.reskin = 0 # 0 = original, 1 = reskin

        if story_part == -1:
            # this is the arcade mode
            self.start_stage = 1
            self.last_stage = 3
            self.arcade_mode = True
        elif story_part == 1:
            # only story part 1 does not have advanced features
            self.advanced_features = False
            self.start_stage = 1
            self.last_stage = 1
        elif story_part == 2:
            self.start_stage = 2
            self.last_stage = 2
        elif story_part == 3:
            # apply reskin in julia's scene
            self.reskin = 1
            self.start_stage = 3
            self.last_stage = 3


    def get_layer(self, layer_name=LayerName.FOREGROUND):
        name = layer_name.value if isinstance(layer_name, LayerName) else layer_name
        if name == LayerName.BACKGROUND.value:
            return self._background_layer
        elif name == LayerName.EFFECTS_BACK.value:
            return self._effects_back_layer
        elif name == LayerName.FOREGROUND.value:
            return self._foreground_layer
        elif name == LayerName.EFFECTS_FRONT.value:
            return self._effects_front_layer
        elif name == LayerName.UI.value:
            return self._ui_layer
        else:
            return None


    def set_state(self, value):
        self._state = value

    def current_screen_scale(self):
        return pygame.display.get_window_size()[0] / self._screen.get_width()

    @property
    def state(self):
        return self._state

    @property
    def screen(self):
        return self._game_space

    # Time properties
    @property
    def current_frame(self):
        return self._current_frame

    @property
    def unscaled_frame(self):
        return self._unscaled_frame

