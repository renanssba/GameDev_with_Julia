import pygame

from constants import GameConstants
from game_context import LayerName
from sound_manager import SfxType
from ui_object import UiObject, UiLabel, UiOverlay



class UiPanel(UiObject):
    def __init__(self, title, options_list, context):
        super().__init__(0, 0, None, context)
        self.body.width = self.context.screen.width
        self.body.height = self.context.screen.height
        self.layer_name = LayerName.UI
        
        # Cursor
        self.cursor = 0
        self.highlight_cursor = True
        self.spacebar_confirms_input = True

        # Option Labels
        labels_block_height = 0
        self.options = options_list
        for i, text in enumerate(self.options):
            pos_x = self.context.screen.width/2
            pos_y = self.context.screen.height*0.65 + i * 36
            self.options[i].ui_label.set_body_center(pos_x, pos_y)
            labels_block_height += 36 
        self.offset_options_labels(0, -labels_block_height/2)

        if title is not None:
            self.title = UiLabel(self.body.width/2, 30, title, context.ui_font_bold, context)
            self.title.update_text_color(GameConstants.COLOR_GAME_SPACE_BORDER.value)
            self.title.align_body_left()
        else:
            self.title = None
        
        self.overlay = UiOverlay(context, self.layer_name, (0, 0, 0, 128))


    def show_panel(self):
        self.cursor = 0
        pass
    
    def hide_panel(self):
        pass
    

    ### RENDERING ###
    def execute_render(self):
        if self.overlay is not None:
            self.overlay.execute_render()
        if self.title is not None:
            self.title.execute_render()
        for i, option in enumerate(self.options):
            if i == self.cursor and self.highlight_cursor:
                option.ui_label.update_text_color(self.get_current_selected_color())
            else:
                option.ui_label.update_text_color(GameConstants.COLOR_UI_BASIC.value)
            option.ui_label.execute_render()

    def get_current_selected_color(self):
        # Alternates between two colors every X unscaled frames
        frame_period = 16
        color_index = (self.context.unscaled_frame // frame_period) % 2
        if color_index == 0:
            return GameConstants.COLOR_UI_SELECTED.value
        else:
            return GameConstants.COLOR_UI_SELECTED_2.value

    
    def offset_options_labels(self, offset_x, offset_y):
        for option in self.options:
            option.ui_label.body.x += offset_x
            option.ui_label.body.y += offset_y
    

    ### INPUT PROCESSING ###
    def process_inputs(self):
        for event in pygame.event.get():
            self.process_generic_inputs(event)
            self.process_panel_specific_inputs(event)
            self.process_debug_inputs(event)
            if len(self.options) > 0:
                self.process_navigation_inputs(event)
        
        for obj in self.context.game_objects:
            obj.process_inputs()

    def process_panel_specific_inputs(self, event):
        pass

    def process_generic_inputs(self, event):
        if event.type == pygame.QUIT:
            self.context.game_controller.close_all_panels()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F12:
                self.toggle_debug() # toggle debug mode

        # DEFINE CURRENT PLAYER INPUT TYPE
        if event.type == pygame.KEYDOWN:
            self.context.player.keyboard_used()
            return
        if event.type == pygame.MOUSEMOTION:
            self.context.player.mouse_moved()
        
        if self.context.debug:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_MINUS:
                    self.context.player.increase_size(-16, 0)
                if event.key == pygame.K_EQUALS:
                    self.context.player.increase_size(16, 0)
                return

    def toggle_debug(self):
        self.context.debug = not self.context.debug # toggle debug mode

    def process_debug_inputs(self, event):
        if not self.context.debug:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                for i, panel in enumerate(self.context.game_controller.panel_list):
                    title_text = panel.title.text if getattr(panel, "title", None) is not None else panel.__class__.__name__
                    print("Panel List["+str(i)+"]: "+title_text) 


    def process_navigation_inputs(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.spacebar_confirms_input:
                self.confirm_input()
            if event.key == pygame.K_RETURN:
                self.confirm_input()
            if event.key == pygame.K_ESCAPE:
                self.cancel_input()
            if event.key == pygame.K_UP:
                self.move_cursor(-1)
            if event.key == pygame.K_DOWN:
                self.move_cursor(1)

        if event.type == pygame.MOUSEMOTION:
            for option in self.options:
                if self.check_if_option_is_hovered(option):
                    self.select_by_hover(self.options.index(option))
                    break
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.check_if_option_is_hovered(self.options[self.cursor]):
                self.confirm_input()
                

    def check_if_option_is_hovered(self, option):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_x = mouse_pos[0] - self.context.screen.x
        mouse_pos_y = mouse_pos[1] - self.context.screen.y
        if option.ui_label.body.collidepoint(mouse_pos_x, mouse_pos_y):
            return True
        return False

    def select_by_hover(self, new_index):
        if new_index != self.cursor:
            self.context.sound_manager.play_sfx(SfxType.UI_SELECT)
            self.cursor = new_index
    
    def move_cursor(self, direction):
        if len(self.options) == 0:
            return
        self.context.sound_manager.play_sfx(SfxType.UI_SELECT)
        self.cursor += direction
        if self.cursor < 0:
            self.cursor = len(self.options) - 1
        if self.cursor >= len(self.options):
            self.cursor = 0

    def confirm_input(self):
        self.context.sound_manager.play_sfx(SfxType.UI_CONFIRM)
        self.options[self.cursor].function()

    def cancel_input(self):
        self.context.sound_manager.play_sfx(SfxType.UI_BACK)
        # TODO: Implement cancel input

    def close_panel(self):
        self.context.game_controller.close_current_panel()
