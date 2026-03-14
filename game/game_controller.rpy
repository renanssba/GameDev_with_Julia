init -1 python:
    import pygame
    from renpy.display.core import IgnoreEvent
    from paddle import Paddle
    from game_object import GameObject
    from game_context import GameContext
    from constants import GameConstants
    from sound_manager import SoundManager
    from game_context import GameState
    import renpy.display.im as im

    class GameController(renpy.Displayable):
        def __init__(self):
            super(GameController, self).__init__()
            self.game = GameContext(
                GameConstants.WIDTH.value,
                GameConstants.HEIGHT.value,
                GameConstants.BRICK_WIDTH.value * GameConstants.BRICK_COLUMNS.value,
                GameConstants.HEIGHT.value,
            )
            self.game.game_controller = self

            # load the paddle image
            self.paddle_sprite = self.load_sprite("paddle_2")
            self.placeholder_sprite = self.load_sprite("placeholder")

            self.print_list_files()

            print("")
            print("")
            print("MY TESTS HAVE SUCCEEDED!!!")
            print("")
            print("")

            # Initialize sound
            self.game.sound_manager = SoundManager()

            # Initialize last frame time
            self.last_st = 0.0

            player_x = self.game.screen.width / 2
            player_y = self.game.screen.height - 30
            # self.paddle = Paddle(player_x, player_y, self.game)
            self.paddle = GameObject(player_x, player_y, "brickA_", self.game)

        def print_list_files(self):
            list_of_files = renpy.list_files()
            for file in list_of_files:
                print("file: ", file)
            print("total files: ", len(list_of_files))

        def load_sprite(self, img_name):
            sprite_path = f"sprites/{img_name}.png"
            if renpy.loader.loadable(sprite_path):
                loaded = renpy.load_surface(sprite_path)
                print(f"{img_name} sprite loaded successfully. size: ", loaded.get_size())
                return loaded
            else:
                print(f"{img_name} is not loadable")
                return None


        def is_paused(self):
            return self.game._state == GameState.PAUSED

        def is_running(self):
            return self.game._state == GameState.RUNNING


        # Game loop (Ren'Py chama render a cada frame)
        def render(self, w, h, st, at):

            # tick frame
            self.tick_frame(w, h, st, at)

            # update all game objects
            self.update(self.game.delta_time)

            # render all game objects
            self.render_everything(w, h)

            return self.game.main_render

        def visit(self):
            return [self.paddle.img]



        def is_still_running(self):
            return True

        def update(self, delta_time):
            self.paddle.process_inputs()
            self.paddle.apply_physics(delta_time)

        def render_everything(self, w, h):
            print("context frame: ", self.game.current_frame, " paddle frame: ", self.paddle.current_frame_number())

            # create main renpy Render
            self.game.main_render = renpy.Render(w, h)

            # renderizar objects
            self.paddle.execute_render()
            # self.game.main_render.blit(paddle_render, (int(self.paddle.body.x), int(self.paddle.body.y)))

            return self.game.main_render


        def tick_frame(self, w, h, st, at):
            # game context variables
            self.game.w = w
            self.game.h = h
            self.game.st = st
            self.game.at = at
            self.game.delta_time = float(st) - float(self.last_st)

            self.game._unscaled_frame += 1

            self.game.delta_time = self.game._clock.tick(60) / 1000
            self.game.delta_time = max(0.01, min(0.1, self.game.delta_time))

            # TODO: re-implement hitstop
            # if self.effect_controller.has_effect(EffectType.HITSTOP):
            #     intensity = self.effect_controller.get_effect(EffectType.HITSTOP).intensity
            #     # intensity = freeze duration in frames
            #     # self.game._clock.tick(60)
            #     time.sleep(intensity / 60.0)
            #     return
            
            if not self.is_running():
                return
            self.game._current_frame += 1

            self.last_st = st
            renpy.redraw(self, 0)


        def event(self, ev, x, y, st):
            if hasattr(ev, "type"):
                if ev.type == pygame.KEYUP:
                    if getattr(ev, "key", None) == pygame.K_RIGHT:
                        self.game.right_pressed = False
                    elif getattr(ev, "key", None) == pygame.K_LEFT:
                        self.game.left_pressed = False

                if ev.type == pygame.KEYDOWN:
                    if getattr(ev, "key", None) == pygame.K_RIGHT:
                        self.game.right_pressed = True
                    elif getattr(ev, "key", None) == pygame.K_LEFT:
                        self.game.left_pressed = True
                    elif getattr(ev, "key", None) == pygame.K_SPACE:
                        self.paddle.jump()
                    elif getattr(ev, "key", None) == pygame.K_ESCAPE:
                        renpy.end_interaction("quit_minigame")
            return None
            # raise IgnoreEvent()


        def debug_event(self, ev):
            # debug: inspeciona o objeto de evento do Ren'Py
            print("=== EVENT DEBUG START ===")
            print(f"repr(ev) = {ev!r}")
            print(f"type(ev) = {type(ev)}")
            print(f"x={x}, y={y}, st={st}")

            # alguns atributos comuns de eventos pygame/renpy
            if hasattr(ev, "type"):
                print(f"ev.type = {ev.type}")
            if hasattr(ev, "key"):
                print(f"ev.key = {getattr(ev, 'key', None)}")
            if hasattr(ev, "mod"):
                print(f"ev.mod = {getattr(ev, 'mod', None)}")
            if hasattr(ev, "pos"):
                print(f"ev.pos = {getattr(ev, 'pos', None)}")
            if hasattr(ev, "button"):
                print(f"ev.button = {getattr(ev, 'button', None)}")

            # lista alguns nomes de atributos disponíveis (limitado para não spammar)
            try:
                attr_names = [name for name in dir(ev) if not name.startswith("_")]
                print("dir(ev) subset =", attr_names[:20])
            except Exception as e:
                print("dir(ev) error:", e)

            print("=== EVENT DEBUG END ===")
