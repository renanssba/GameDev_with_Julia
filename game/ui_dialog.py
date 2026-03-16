from particle import TextParticle
from vector2 import Vector2
from ui_object import UiObject

class UiDialog(TextParticle):
    def __init__(self, context, speaker, text, appear_time_in_sec, show_time_in_sec = 3):
        time_to_appear = appear_time_in_sec*60
        time_showing = show_time_in_sec*60
        super().__init__(context, 0, 0, text, time_to_appear + time_showing, 12)
        
        self.set_body_center(-context.screen.x + 90, context.screen.h/2 + 60)
        self.time_to_appear = time_to_appear

        self.velocity = Vector2(0, 0)

        self.face = UiObject(self.body.x-80, self.body.y - 26, "face_"+speaker, context)

    def execute_render(self):
        if self.lifetime_current >= self.time_to_appear:
            self.face.execute_render()
            super().execute_render()

