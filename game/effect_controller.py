import pygame
from effects import Effect, EffectType
from game_context import LayerName
from constants import GameConstants


class EffectController:
    def __init__(self, myObject):
        self.myObject = myObject
        if hasattr(myObject, 'context'):
            self.context = myObject.context
        else:
            self.context = myObject.game
        self.effect_list = []

    def add_effect(self, effect_type, intensity, duration, sprite_name = None):
        for effect in self.effect_list:
            if effect.effect_type == effect_type:
                effect.update_duration(duration)
                return
        
        new_effect = Effect(effect_type, intensity, duration, self.context)
        self.effect_list.append(new_effect)
        self.myObject.apply_effect(effect_type)
        if(sprite_name != None):
            self.create_effect_bar(new_effect, sprite_name)


    def update(self):
        for effect in self.effect_list:
            if effect.should_die():
                self.effect_list.remove(effect)
                self.myObject.remove_effect(effect.effect_type)
                self.context.game_controller.gameplay_panel.remove_effect_bar(effect)
            effect.update()

    def create_effect_bar(self, effect, sprite_name):
        from ui_object import EffectDurationBar
        new_duration_bar = EffectDurationBar(effect, sprite_name, self.context)
        self.context.game_controller.gameplay_panel.add_effect_bar(new_duration_bar)
    
    def has_effect(self, effect_type):
        return self.get_effect(effect_type) is not None

    def get_effect(self, effect_type):
        for effect in self.effect_list:
            if effect.effect_type == effect_type:
                return effect
        return None

    def has_effect_activating(self, effect_type):
        effect = self.get_effect(effect_type)
        return effect is not None and effect.is_activation_frame()


    def clear(self):
        self.effect_list.clear()
