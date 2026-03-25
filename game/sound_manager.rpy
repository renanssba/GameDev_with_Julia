init -2 python:
    import time
    import math
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

            # Hora em que cada canal sfx começou a tocar (para escolher o mais antigo quando todos ocupados)
            self.sfx_channel_start = {}

            master_volume = preferences.volumes["main"]
            music_volume = preferences.volumes["music"]
            sfx_volume = preferences.volumes["sfx"]


        def get_all_volumes(self):
            return {
                "main": self.mixer_to_bar_fraction(preferences.volumes["main"]),
                "music": self.mixer_to_bar_fraction(preferences.volumes["music"]),
                "sfx": self.mixer_to_bar_fraction(preferences.volumes["sfx"]),
            }

        
        def mixer_to_bar_fraction(self, mixer_value):
            """
            Recebe volume do mixer (0..1) e retorna a fração da barra (0..1),
            no sistema de sliders de volume do Ren'Py.
            """
            if mixer_value <= 0:
                return 0.0

            if renpy.config.quadratic_volumes:
                # MixerValue: mixer = t^2 -> t = sqrt(mixer)
                return max(0.0, min(1.0, math.sqrt(mixer_value)))

            # MixerValue (quadratic_volumes=False):
            # get_mixer() faz: bar_value_db = 20*log10(mixer) + R, onde R=volume_db_range
            # A barra vai de 0..R, então a fração é bar_value_db / R.
            R = renpy.config.volume_db_range
            bar_value_db = 20 * math.log10(mixer_value) + R
            return max(0.0, min(1.0, bar_value_db / R))

        def bar_fraction_to_mixer(self, bar_fraction):
            """
            Recebe a porcentagem/fração da barra (0..1 ou 0..100) e retorna o valor do mixer (0..1).
            """
            # Aceita tanto 0..1 quanto 0..100
            t = float(bar_fraction)
            if t > 1.0:
                t = t / 100.0

            t = max(0.0, min(1.0, t))
            if t <= 0.0:
                return 0.0

            if renpy.config.quadratic_volumes:
                # MixerValue: set_mixer() faz mixer = t^2
                return t * t

            # MixerValue (quadratic_volumes=False):
            # set_mixer() faz:
            #   value = bar_value_db - R
            #   mixer = 10 ** (value / 20)
            # onde bar_value_db = t * R.
            R = renpy.config.volume_db_range
            bar_value_db = t * R
            return pow(10, (bar_value_db - R) / 20)

        def first_free_sfx_channel(self):
            """Retorna o nome do primeiro canal sfx livre, ou None se todos ocupados."""
            for ch in self.SFX_CHANNELS:
                if renpy.sound.get_playing(channel=ch) is None:
                    return ch
            return None

        def oldest_busy_sfx_channel(self):
            """Retorna o canal sfx que começou a tocar mais cedo (entre os ocupados)."""
            oldest_ch = None
            oldest_t = None
            for ch in self.SFX_CHANNELS:
                if renpy.sound.get_playing(channel=ch) is not None:
                    t = self.sfx_channel_start.get(ch, 0)
                    if oldest_t is None or t < oldest_t:
                        oldest_t = t
                        oldest_ch = ch
            return oldest_ch

        def play_sfx(self, sfx_type):
            """Toca um SFX no primeiro canal livre. Se todos ocupados, para o que começou mais cedo e usa o canal."""
            ch = self.first_free_sfx_channel()
            if ch is None:
                ch = self.oldest_busy_sfx_channel()
                if ch is not None:
                    renpy.sound.stop(channel=ch)
            if ch is None:
                return
            name = sfx_type.value
            path = "sfx/" + name + ".ogg"
            if renpy.loader.loadable(path):
                renpy.sound.play(path, channel=ch)
                self.sfx_channel_start[ch] = time.time()

        def get_music_base(self, sfx_type):
            base = sfx_type.value
            if base.endswith("_intro"):
                return base[:-6]
            if base.endswith("_loop"):
                return base[:-5]
            return base

        def play_music(self, sfx_type):
            """Toca música: intro (1x) + loop (∞). Se não houver intro, só loop."""
            base = self.get_music_base(sfx_type)

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

        def set_volumes(self, master_slider_volume, sfx_slider_volume, music_slider_volume):
            """Volumes 0–10. Aplica ao Ren'Py (preferences) e aos canais."""
            preferences.volumes["main"] = self.bar_fraction_to_mixer(master_slider_volume)
            preferences.volumes["music"] = self.bar_fraction_to_mixer(music_slider_volume)
            preferences.volumes["sfx"] = self.bar_fraction_to_mixer(sfx_slider_volume)

            renpy.music.set_volume(preferences.volumes["music"], channel="music")
            for ch in self.SFX_CHANNELS:
                renpy.music.set_volume(preferences.volumes["sfx"], channel=ch)
