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

class LayerName(Enum):
    BACKGROUND = "background"
    EFFECTS_BACK = "effects_back"
    FOREGROUND = "foreground"
    EFFECTS_FRONT = "effects_front"
    UI = "ui"


class GameContext:
    def __init__(self, width, height, game_space_width, game_space_height):
        # Guardar resolução base para permitir trocar escala depois
        self._base_width = width
        self._base_height = height

        # self._screen = pygame.display.set_mode((width, height), pygame.SCALED)

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

        # Current Stage
        self.stage_id = 1

        # Game Controller
        self.game_controller = None


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

    def resize(self, scale: int):
        """Altera a resolução da janela mantendo o game space centralizado."""
        if scale < 1:
            scale = 1
        width = int(self._base_width * scale)
        height = int(self._base_height * scale)

        # Atualiza janela
        self._screen = pygame.display.set_mode((width, height))

        # Recria camadas com o novo tamanho
        self._background_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self._effects_back_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self._foreground_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self._effects_front_layer = pygame.Surface((width, height), pygame.SRCALPHA)
        self._ui_layer = pygame.Surface((width, height), pygame.SRCALPHA)

        # Reposiciona o game space mantendo largura/altura atuais
        gs_w = self._game_space.width
        gs_h = self._game_space.height
        self._game_space.x = (width - gs_w) / 2
        self._game_space.y = (height - gs_h) / 2

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

