init -1 python:
    import os
    import random
    import pygame
    from renpy.display.core import IgnoreEvent
    from paddle import Paddle
    from ball import Ball
    from brick import Brick
    from game_object import GameObject
    from game_context import GameContext
    from constants import GameConstants
    from sound_manager import SoundManager
    from game_context import GameState
    from stage_controller import StageController
    from effects import EffectType
    from effect_controller import EffectController
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
            
            # Initialize sound
            self.game.sound_manager = SoundManager()

            # DEBUG PRINT ALL FILES
            # self.print_list_files()
            
            # Setup stage (player, sound, level)
            self.stage_controller = StageController(self.game)
            self.stage_controller.setup(self.game.stage_id)

            # Initialize game-wide effects
            self.effect_controller = EffectController(self)

            # Initialize last frame time
            self.last_st = 0.0

            self.current_panel = None

            # DEBUG
            self.game.debug = False


        def is_paused(self):
            return self.game._state == GameState.PAUSED

        def is_running(self):
            return self.game._state == GameState.RUNNING


        # Game loop (Ren'Py chama render a cada frame)
        def render(self, w, h, st, at):
            # tick frame
            self.tick_frame(w, h, st, at)

            # Atualiza música (transição de intro para loop infinito)
            if self.game.sound_manager is not None:
                self.game.sound_manager.update()

            # processar inputs do painel atual
            if self.current_panel is not None:
                self.current_panel.process_inputs()

            # update all game objects
            if self.is_running():
                self.apply_physics_to_all()
                self.check_victory()
                self.check_defeat_or_revive()

            # cria main_render que conterá o jogo inteiro
            self.game.main_render = renpy.Render(self.game.w, self.game.h)

            # cada GameObject faz blit de si no main_render.
            self.render_everything()

            # retorna o main_render para o Ren'Py renderizar
            return self.game.main_render

        def visit(self):
            objs = []
            for obj in self.game.game_objects:
                objs.extend(obj.visit())
            return objs



        def is_still_running(self):
            return True

        def multiply_ball(self):
            free_balls = []
            all_balls = []
            for obj in self.game.game_objects:
                if isinstance(obj, Ball):
                    all_balls.append(obj)
                    if not obj.stuck_to_paddle:
                        free_balls.append(obj)
            # priorize to multiply free balls
            if len(free_balls) > 0:
                random_ball = random.choice(free_balls)
                random_ball.multiply_ball()
                return
            # if no free balls, multiply a random stuck ball
            if len(all_balls) > 0:
                random_ball = random.choice(all_balls)
                random_ball.be_launched()
                random_ball.multiply_ball()
    
        def check_victory(self):
            if not self.any_of_this_type(Brick):
                self.victory_panel.options[1].ui_label.update_text(f"Score {self.game.score}")
                self.set_game_state(GameState.VICTORY)

        def check_defeat_or_revive(self):
            if not self.any_of_this_type(Ball):
                if self.game.lives > 0:
                    self.game.lives -= 1
                    self.game.player.prepare_ball()
                else:
                    self.defeat_panel.options[2].ui_label.update_text(f"Score {self.game.score}")
                    self.set_game_state(GameState.DEFEAT)


        ### TIMED EFFECTS ###
        def apply_effect(self, effect_type):
            match effect_type:
                case EffectType.SLOW_BALLS:
                    self.game.time_scale *= GameConstants.SLOW_FACTOR.value
                case EffectType.HASTE_BALLS:
                    self.game.time_scale *= GameConstants.HASTE_FACTOR.value

        def remove_effect(self, effect_type):
            match effect_type:
                case EffectType.SLOW_BALLS:
                    self.game.time_scale /= GameConstants.SLOW_FACTOR.value
                case EffectType.HASTE_BALLS:
                    self.game.time_scale /= GameConstants.HASTE_FACTOR.value


        def any_of_this_type(self, type):
            for obj in self.game.game_objects:
                if isinstance(obj, type):
                    return True
            return False
        
    

        def gain_score(self, amount, obj):
            self.game.score += amount
            # self.gameplay_panel.update_ui()
            if obj is not None:
                obj.spawn_text_particle(f"+{amount}")
            else:
                self.game.player.spawn_text_particle(f"+{amount}")
            return

        def update_ui(self):
            # self.gameplay_panel.update_ui()
            pass
        

        ### PHYSICS ###
        def apply_physics_to_all(self):
            for obj in self.game.game_objects:
                obj.apply_physics()
                obj.process_inputs()
            self.effect_controller.update()
            
        
        ### RENDERING ###
        def render_everything(self):
            # renderizar objects
            for obj in self.game.game_objects:
                obj.execute_render()


        def tick_frame(self, w, h, st, at):
            # game context variables
            self.game.w = w
            self.game.h = h
            self.game.st = st
            self.game.at = at
            self.game.delta_time = float(st) - float(self.last_st)
            # print("st: ", st, " last_st: ", self.last_st, " delta_time: ", self.game.delta_time)
            self.last_st = st

            self.game._unscaled_frame += 1

            self.game.delta_time = self.game._clock.tick(60) / 1000
            self.game.delta_time = max(0.01, min(0.1, self.game.delta_time))

            # TODO: re-implement hitstop
            if self.effect_controller.has_effect(EffectType.HITSTOP):
                intensity = self.effect_controller.get_effect(EffectType.HITSTOP).intensity
                # intensity = freeze duration in frames
                # self.game._clock.tick(60)
                renpy.redraw(self, intensity / 60.0)
                return
            
            renpy.redraw(self, 0)

            if not self.is_running():
                return
            self.game._current_frame += 1


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
                        self.game.player.action_button_pressed()
                    elif getattr(ev, "key", None) == pygame.K_ESCAPE:
                        renpy.end_interaction("quit_minigame")
            return None


        ### DEBUG FUNCTIONS ###
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

        def print_list_files(self):
            print("")
            print("")
            print("LISTING ALL FILES IN THE GAME FOLDER!!!")
            print("")
            print("")
            list_of_files = renpy.list_files()
            for file in list_of_files:
                print("file: ", file)
            print("total files: ", len(list_of_files))

