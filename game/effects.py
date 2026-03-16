from enum import Enum

class EffectType(Enum):
    SCALE = "scale"
    FLASH = "flash"
    FADE = "fade"
    HITSTOP = "hitstop"

    ENLARGE_PADDLE = "enlarge_paddle"
    SHRINK_PADDLE = "shrink_paddle"
    SHOOTING_PADDLE = "shots"
    SLOW_BALL = "slow_time"
    HASTE_BALL = "haste_balls"
    STICKY_PADDLE = "sticky_paddle"

    ACTIVATE_RESKIN_ON_END = "activate_reskin_on_effect"

class Effect:
    def __init__(self, effect_type: EffectType, intensity, duration, context):
        self.effect_type = effect_type
        self.intensity = intensity
        self.duration = duration
        self.current_frame = 0
        self.tick = 60
        self.context = context

    def update_duration(self, new_duration):
        if self.duration - self.current_frame < new_duration:
            self.duration = new_duration
            self.current_frame = 0

    def update(self):
        self.current_frame += 1

    def is_activation_frame(self):
       return self.current_frame % self.tick == 0


    def should_die(self):
        return self.current_frame > self.duration
