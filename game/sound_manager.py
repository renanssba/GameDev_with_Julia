import pygame
import renpy
from enum import Enum


class SfxType(Enum):
    EXPLOSION = "explosion"
    COIN = "itm_coin_get"
    BALL_LAUNCH = "ball_launch"
    BALL_MISS = "ball_miss"
    BALL_BOUNCE = "ball_bounce"

    BALL_BOUNCE_PADDLE = "collect"
    BALL_HIT_PADDLE = "ball_impact"
    BALL_BOUNCE_POWER = "ball_power"
    FIRE = "fire"
    JUMP = "jump32"

    UI_SELECT = "ui_select"
    UI_CONFIRM = "ui_confirm"
    UI_FORBIDDEN = "ui_forbidden"
    UI_BACK = "ui_back"
    UI_PAUSE = "ui_pause0"
    UI_UNPAUSE = "ui_pause1"

    GAME_OVER = "game_over"
    
    BRICK_HIT = "obs_default_hit"
    BRICK_DESTROY = "obs_default_destroy"

    POWERUP_GET = "powerup_got"
    MALUS_GET = "malus_got"

    GAMEPLAY_MUSIC = "gameplay"
    MENU_MUSIC = "menu"
    VICTORY_MUSIC = "victory"
    DEFEAT_MUSIC = "defeat"



class SoundManager:
    def __init__(self):
        self.current_music = None  # current base name (without _intro/_loop)
        self._music_state = None   # None, "intro" or "loop"

        # Volumes (0.0–1.0). Master is a multiplier for both SFX and music.
        self.master_volume = 0.7
        self.sfx_volume = 0.7
        self.music_volume = 0.7

    def play_sfx(self, sfx_type: SfxType):
        """Plays an SFX by enum value."""
        name = sfx_type.value
        sfx_path = "sfx/"+name+".ogg"
        if renpy.loader.loadable(sfx_path):
            return renpy.audio.sound.play(sfx_path, channel="audio")
        else:
            print("SFX not found:", name)
            return None

    def _get_music_base(self, sfx_type: SfxType) -> str:
        """Extracts the base name without _intro/_loop suffixes."""
        base = sfx_type.value
        if base.endswith("_intro"):
            return base[:-6]
        if base.endswith("_loop"):
            return base[:-5]
        return base

    def play_music(self, sfx_type: SfxType):
        """
        Plays music in two parts: intro (1x) + loop (∞).
        If the intro file does not exist, only the loop is played in loop infinity.
        """
        base = self._get_music_base(sfx_type)

        # already playing this music
        if self.current_music == base and self._music_state in ("intro", "loop"):
            return

        intro_path = f"songs/{base}_intro.mp3"
        loop_path = f"songs/{base}_loop.mp3"

        if renpy.loader.loadable(intro_path):
            renpy.audio.music.play(intro_path, loop=False)
            self.current_music = base
            self._music_state = "intro"
        elif renpy.loader.loadable(loop_path):
            renpy.audio.music.play(loop_path, loop=True)
            self.current_music = base
            self._music_state = "loop"
        else:
            # no file found
            self.current_music = None
            self._music_state = None
        
    def update(self):
        """Updates the music state: when the intro ends, starts the loop infinitely."""
        if self._music_state != "intro":
            return
        if renpy.audio.music.get_playing(channel="music") is None:
            base = self.current_music
            if base is None:
                self._music_state = None
                return
            loop_path = f"songs/{base}_loop.mp3"
            if renpy.loader.loadable(loop_path):
                renpy.audio.music.play(loop_path, channel="music", loop=True)
                self._music_state = "loop"
            else:
                self._music_state = None

    def stop_music(self):
        renpy.audio.music.stop(channel="music")
        self.current_music = None
        self._music_state = None

    def set_volumes(self, master_steps: int, sfx_steps: int, music_steps: int):
        """
        Updates volumes: each value is from 0 to 10.
        - master: global multiplier
        - sfx: relative volume of sound effects
        - music: relative volume of music
        """
        # Normalize to 0.0 – 1.0
        self.master_volume = master_steps / 10.0
        self.sfx_volume = sfx_steps / 10.0
        self.music_volume = music_steps / 10.0

        # Apply to current music (if any)
        renpy.audio.music.set_volume(self.effective_music_volume(), channel="music")
        renpy.audio.sound.set_volume(self.effective_sfx_volume(), channel="audio")

    def effective_sfx_volume(self):
        return self.master_volume * self.sfx_volume

    def effective_music_volume(self):
        return self.master_volume * self.music_volume
