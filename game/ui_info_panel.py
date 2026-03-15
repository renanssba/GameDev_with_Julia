import pygame

from ui_panel import UiPanel
from ui_object import UiOption


class UiInfoPanel(UiPanel):
    def __init__(self, font, text_array, context):
        options_list = []
        for text in text_array:
            options_list.append(UiOption(text, self.close_panel, context))
        super().__init__("", options_list, context)
        self.offset_options_labels(0, -20)
        self.highlight_cursor = False
