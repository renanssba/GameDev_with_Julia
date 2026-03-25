# SoundManager e SfxType - áudio via Ren'Py (music/sound)
# 12 canais SFX (sfx0–sfx11); play_sfx usa o primeiro canal livre.
# Uso: context.sound_manager.play_music(SfxType.GAMEPLAY_MUSIC), play_sfx(SfxType.COIN), etc.

init -2 python:
    import time
    from enum import Enum

    # Registra 12 canais de SFX (mixer "sfx", sem loop) para tocar vários efeitos ao mesmo tempo
    for i in range(12):
        renpy.music.register_channel("sfx" + str(i), "sfx", loop=False)

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
        JULIA_MODE_MUSIC = "julia_mode"

    class SoundManager(object):
        SFX_CHANNELS = ["sfx" + str(i) for i in range(12)]  # sfx0 até sfx11

        def __init__(self):
            self.current_music = None
            self._music_state = None  # None, "intro" or "loop"

            self.master_volume = 0.7
            self.sfx_volume = 0.7
            self.music_volume = 0.7
            # Hora em que cada canal sfx começou a tocar (para escolher o mais antigo quando todos ocupados)
            self._sfx_channel_start = {}

            master_volume = preferences.volumes["main"]
            music_volume = preferences.volumes["music"]
            sfx_volume = preferences.volumes["sfx"]
            print(f">> SFX volume: {sfx_volume}, Music volume: {music_volume}, Master volume: {master_volume}")
        
        def get_all_volumes(self):
            return preferences.volumes

        def _first_free_sfx_channel(self):
            """Retorna o nome do primeiro canal sfx livre, ou None se todos ocupados."""
            for ch in self.SFX_CHANNELS:
                if renpy.sound.get_playing(channel=ch) is None:
                    return ch
            return None

        def _oldest_busy_sfx_channel(self):
            """Retorna o canal sfx que começou a tocar mais cedo (entre os ocupados)."""
            oldest_ch = None
            oldest_t = None
            for ch in self.SFX_CHANNELS:
                if renpy.sound.get_playing(channel=ch) is not None:
                    t = self._sfx_channel_start.get(ch, 0)
                    if oldest_t is None or t < oldest_t:
                        oldest_t = t
                        oldest_ch = ch
            return oldest_ch

        def play_sfx(self, sfx_type):
            """Toca um SFX no primeiro canal livre. Se todos ocupados, para o que começou mais cedo e usa o canal."""
            ch = self._first_free_sfx_channel()
            if ch is None:
                ch = self._oldest_busy_sfx_channel()
                if ch is not None:
                    renpy.sound.stop(channel=ch)
            if ch is None:
                return
            name = sfx_type.value
            path = "sfx/" + name + ".ogg"
            if renpy.loader.loadable(path):
                renpy.sound.play(path, channel=ch)
                self._sfx_channel_start[ch] = time.time()

        def _get_music_base(self, sfx_type):
            base = sfx_type.value
            if base.endswith("_intro"):
                return base[:-6]
            if base.endswith("_loop"):
                return base[:-5]
            return base

        def play_music(self, sfx_type):
            """Toca música: intro (1x) + loop (∞). Se não houver intro, só loop."""
            base = self._get_music_base(sfx_type)

            if self.current_music == base and self._music_state in ("intro", "loop"):
                return

            intro_path = "songs/" + base + "_intro.mp3"
            loop_path = "songs/" + base + "_loop.mp3"

            if renpy.loader.loadable(intro_path):
                renpy.music.play(intro_path, channel="music", loop=False)
                self.current_music = base
                self._music_state = "intro"
            elif renpy.loader.loadable(loop_path):
                renpy.music.play(loop_path, channel="music", loop=True)
                self.current_music = base
                self._music_state = "loop"
            else:
                self.current_music = None
                self._music_state = None

        def update(self):
            """Quando o intro termina, inicia o loop infinito."""
            if self._music_state != "intro":
                return
            if renpy.exports.music.get_playing(channel="music") is None:
                base = self.current_music
                if base is None:
                    self._music_state = None
                    return
                loop_path = "songs/" + base + "_loop.mp3"
                if renpy.loader.loadable(loop_path):
                    renpy.exports.music.play(loop_path, channel="music", loop=True)
                    self._music_state = "loop"
                else:
                    self._music_state = None

        def stop_music(self):
            renpy.exports.music.stop(channel="music")
            self.current_music = None
            self._music_state = None

        def set_volumes(self, master_steps, sfx_steps, music_steps):
            """Volumes 0–10. Aplica ao Ren'Py (preferences) e aos canais."""
            self.master_volume = master_steps / 10.0
            self.sfx_volume = sfx_steps / 10.0
            self.music_volume = music_steps / 10.0

            vol_music = self.master_volume * self.music_volume
            vol_sfx = self.master_volume * self.sfx_volume

            renpy.music.set_volume(vol_music, channel="music")
            for ch in self.SFX_CHANNELS:
                renpy.music.set_volume(vol_sfx, channel=ch)

        def effective_sfx_volume(self):
            return self.master_volume * self.sfx_volume

        def effective_music_volume(self):
            return self.master_volume * self.music_volume
