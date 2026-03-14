from enum import Enum


class GameConstants(Enum):
    # Game
    WIDTH = 480
    HEIGHT = 270
    INITIAL_LIVES = 3
    MAX_LIVES = 6

    # Bricks
    BRICK_COLUMNS = 10
    BRICK_ROWS = 8
    BRICK_WIDTH = 32
    BRICK_HEIGHT = 16
    BRICK_COIN_CHANCE = 0.3
    BRICK_POWERUP_CHANCE = 0.4

    # Paddle
    PADDLE_WIDTH = 32
    PADDLE_HEIGHT = 8

    # Balls
    BALL_DIAMETER = 8

    # Powerups
    POWERUP_DURATION = 1200
    MALUS_DURATION = 1200
    HASTE_FACTOR = 1.5
    SLOW_FACTOR = 0.5

    # Leaderboard
    LEADERBOARD_MAX_ENTRIES = 10
    LEADERBOARD_MAX_NAME_LENGTH = 14

    # External files and paths
    OPTIONS_FILE = "saves/options.json"
    LEADERBOARD_FILE = "saves/leaderboard.json"

    # Fonts
    UI_FONT_BOLD = "fonts/Baskic8-Bold.otf"
    UI_FONT = "fonts/Baskic8.otf"
    UI_SCORE_FONT = "fonts/Baskic8.otf"

    # Colors
    COLOR_BLACK = (0, 0, 0)
    COLOR_WHITE = (255, 255, 228)
    COLOR_RAW_WHITE = (255, 255, 255)
    COLOR_RAW_BLACK = (0, 0, 0)
    COLOR_UI_BASIC = (255, 255, 228)
    COLOR_UI_SELECTED = (255, 216, 50)
    COLOR_UI_SELECTED_2 = (255, 130, 59)
    COLOR_GAME_SPACE = (0, 0, 30, 255)
    COLOR_GAME_SPACE_BORDER = (28, 146, 167, 255)
    COLOR_TRANSPARENT = (0, 0, 0, 0)
