init -1 python:
    import pygame
    import random
    from constants import GameConstants
    from ball import Ball
    from brick import Brick
    from paddle import Paddle
    from game_context import GameContext, GameState
    from stage_controller import StageController
    from ui_info_panel import UiInfoPanel
    from ui_gameplay_panel import UiGameplayPanel
    from ui_pause_panel import UiPausePanel
    from ui_title_panel import UiTitlePanel
    from ui_options_panel import UiOptionsPanel
    from ui_leaderboard_panel import UiLeaderboardPanel
    from ui_end_card_panel import UiEndCardPanel
    from ui_transition_panel import UiTransitionPanel
    from renpy.store import SoundManager, SfxType
    from effects import EffectType
    from effect_controller import EffectController
    from reskinner import Reskinner
    import renpy.display.im as im
    from renpy.display.core import IgnoreEvent
    from renpy.display.layout import Transform

    class GameController(renpy.Displayable):
        def __init__(self, story_part):
            super(GameController, self).__init__()
            self.game = GameContext(
                GameConstants.WIDTH.value,
                GameConstants.HEIGHT.value,
                GameConstants.BRICK_WIDTH.value * GameConstants.BRICK_COLUMNS.value,
                GameConstants.HEIGHT.value,
                story_part
            )
            self.game.game_controller = self
            
            # Initialize sound
            self.game.sound_manager = SoundManager()

            # Panels first (so they exist even if stage setup fails)
            self.title_ui = UiTitlePanel(self.game)
            self.gameplay_panel = UiGameplayPanel(self.game)
            self.pause_ui = UiPausePanel(self.game)
            self.options_panel = UiOptionsPanel(self.game)
            self.leaderboard_panel = UiLeaderboardPanel(self.game)

            # Initialize game-wide effects
            self.effect_controller = EffectController(self)
            
            # Setup stage (player, sound, level)
            self.stage_controller = StageController(self.game)
            self.stage_controller.reset_stage()

            # End card panels
            self.victory_panel = UiEndCardPanel(self.game.ui_font_bold, ["YOU WIN!", "Score 1000"], self.game)
            self.defeat_panel = UiEndCardPanel(self.game.ui_font_bold, ["GAME OVER...", "Try again", "Score 1000"], self.game)
            # play or stop music when opening those
            self.victory_panel.show_panel = (lambda: self.game.sound_manager.play_music(SfxType.VICTORY_MUSIC))
            # self.defeat_panel.show_panel = (lambda: if self.game.reskin == 0: self.game.sound_manager.stop_music())

            # Transition panels
            transition_data = []
            transition_data.name = "Stage Clear!"
            option = []
            option.name = "Next"
            transition_data.options = [option]
            self.transition_panel = UiTransitionPanel(transition_data, self.game)

            # DEBUG PRINT ALL FILES
            # self.print_list_files()

            # Reskinner
            self.reskinner = None

            # Initialize last frame time
            self.last_st = 0.0

            self.panel_list = []

            # DEBUG
            # self.game.debug = True
            if not self.game.arcade_mode:
                self.open_panel(self.gameplay_panel)
            else:
                self.open_panel(self.title_ui)


        def is_paused(self):
            return self.game._state == GameState.PAUSED

        def is_running(self):
            return self.game._state == GameState.RUNNING

        def tick_frame(self, w, h, st, at):
            # game context variables
            self.game.w = w
            self.game.h = h
            self.game.st = st
            self.game.at = at
            self.game.delta_time = float(st) - float(self.last_st)
            self.last_st = st

            self.game._unscaled_frame += 1

            if self.effect_controller.has_effect(EffectType.HITSTOP):
                intensity = self.effect_controller.get_effect(EffectType.HITSTOP).intensity
                renpy.redraw(self, intensity / 60.0)
                return
            
            # cap FPS at 60
            min_delta_time = 1.0 / 60.0 # cap FPS at 60
            if self.game.delta_time < min_delta_time:
                renpy.redraw(self, min_delta_time - self.game.delta_time)
            else:
                renpy.redraw(self, 0)

            if not self.is_running():
                return
            self.game._current_frame += 1


        # Game loop (Ren'Py chama render a cada frame)
        def render(self, w, h, st, at):
            # tick frame
            self.tick_frame(w, h, st, at)

            # Atualiza música (transição de intro para loop infinito)
            if self.game.sound_manager is not None:
                self.game.sound_manager.update()

            # update all game objects
            if self.is_running():
                self.apply_physics_to_all()
                self.check_victory()
                self.check_defeat_or_revive()

            # cada GameObject faz blit de si no main_render.
            self.render_everything()

            # retorna o main_render para o Ren'Py renderizar
            return self.game.main_render

        def visit(self):
            objs = []
            for obj in self.game.game_objects:
                objs.extend(obj.visit())
            return objs

        


        def gain_score(self, amount, obj):
            self.game.score += amount
            self.gameplay_panel.update_ui()
            if obj is not None:
                obj.spawn_text_particle(f"+{amount}")

        def update_ui(self):
            self.gameplay_panel.update_ui()

        ### PHYSICS ###
        def apply_physics_to_all(self):
            for obj in self.game.game_objects:
                obj.apply_physics()
            self.effect_controller.update()
            if self.reskinner is not None:
                self.reskinner.update()
        
        ### RENDERING ###
        def render_everything(self):
            self.clear_screen()
            # renderizar objects
            for obj in self.game.game_objects:
                obj.execute_render()
            if self.current_panel is not None:
                self.current_panel.execute_render()
            self.merge_all_layers()

        def clear_screen(self):
            # cria main_render que conterá o jogo inteiro
            self.game.main_render = renpy.Render(self.game.w, self.game.h)
            self.game._background_layer = renpy.Render(self.game.w, self.game.h)

            self.game._effects_back_layer = renpy.Render(self.game.w, self.game.h)

            self.game._foreground_layer = renpy.Render(self.game.w, self.game.h)
            self.game._effects_front_layer = renpy.Render(self.game.w, self.game.h)
            self.game._ui_layer = renpy.Render(self.game.w, self.game.h)

            
        def merge_all_layers(self):
            self.game.main_render.blit(self.game._background_layer, (0, 0))
            # effects_back com 50% de opacidade
            effects_back_wrapper = _LayerAsDisplayable(lambda: self.game._effects_back_layer)
            effects_back_with_alpha = renpy.render(Transform(child=effects_back_wrapper, alpha=0.5), self.game.w, self.game.h, self.game.st, self.game.at)
            self.game.main_render.blit(effects_back_with_alpha, (0, 0))

            self.game.main_render.blit(self.game._foreground_layer, (0, 0))
            self.game.main_render.blit(self.game._effects_front_layer, (0, 0))
            self.game.main_render.blit(self.game._ui_layer, (0, 0))



        ### FLOW AND MISC EFFECTS ###
        def set_game_state(self, game_state):
            self.game.set_state(game_state)
            match game_state:
                case GameState.TITLE:
                    self.close_all_panels()
                    self.open_panel(self.title_ui)
                case GameState.RUNNING:
                    self.stage_controller.reset_stage()
                    self.open_panel(self.gameplay_panel)
                case GameState.PAUSED:
                    self.open_panel(self.pause_ui)
                case GameState.OPTIONS:
                    self.open_panel(self.options_panel)
                case GameState.LEADERBOARD:
                    self.open_panel(self.leaderboard_panel)
                case GameState.VICTORY:
                    self.close_all_panels()
                    if self.game.arcade_mode:
                        self.open_panel(self.title_ui)
                    self.open_panel(self.victory_panel)
                case GameState.DEFEAT:
                    self.close_all_panels()
                    if self.game.arcade_mode:
                        self.open_panel(self.title_ui)
                    self.open_panel(self.defeat_panel)
                case GameState.TRANSITION:
                    self.close_all_panels()
                    self.open_panel(self.transition_panel)

        def toggle_reskin(self, time_to_wait=0):
            if self.game.reskin == 0:
                self.game.reskin = 1
            else:
                self.game.reskin = 0

            list_objects = []
            list_objects.extend(self.game.game_objects)
            list_objects.extend(self.gameplay_panel.objects_to_reskin)
            list_objects.extend(self.title_ui.objects_to_reskin)
            list_objects.extend(self.pause_ui.objects_to_reskin)
            list_objects.extend(self.options_panel.objects_to_reskin)
            list_objects.extend(self.leaderboard_panel.objects_to_reskin)
            self.reskinner = Reskinner(self.game, list_objects, time_to_wait)

        @property
        def current_panel(self):
            return self.panel_list[0] if self.panel_list else None

        def open_panel(self, panel):
            self.panel_list.insert(0, panel)
            panel.show_panel()

        def close_current_panel(self):
            if not self.panel_list:
                return
            closing_panel = self.panel_list.pop(0)
            closing_panel.hide_panel()
            if self.panel_list:
                self.panel_list[0].show_panel()
                if self.panel_list[0] == self.gameplay_panel:
                    self.game.set_state(GameState.RUNNING)
            else:
                self.close_all_panels()

        def close_all_panels(self):
            while self.panel_list:
                self.close_current_panel()

        def should_end_minigame(self):
            return self.panel_list == []


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
            if not self.any_of_this_type(Brick) and self.any_of_this_type(Paddle):
                self.victory_panel.options[1].ui_label.update_text(f"Score {self.game.score}")
                self.advance_stage()

        def advance_stage(self):
            print("ADVANCING STAGE. current stage: ", self.game.current_stage, "last stage: ", self.game.last_stage)
            self.game.game_objects = []
            self.game.current_stage += 1
            if self.game.current_stage > self.game.last_stage:
                self.set_game_state(GameState.VICTORY)
            else:
                self.set_game_state(GameState.TRANSITION)

        def check_defeat_or_revive(self):
            if not self.any_of_this_type(Ball) and self.any_of_this_type(Paddle):
                if self.game.lives > 0:
                    self.game.lives -= 1
                    self.game.player.prepare_ball()
                else:
                    self.defeat_panel.options[2].ui_label.update_text(f"Score {self.game.score}")
                    self.set_game_state(GameState.DEFEAT)



        ### TIMED EFFECTS ###
        def apply_effect(self, effect_type):
            match effect_type:
                case EffectType.SLOW_BALL:
                    self.game.time_scale *= GameConstants.SLOW_FACTOR.value
                case EffectType.HASTE_BALL:
                    self.game.time_scale *= GameConstants.HASTE_FACTOR.value

        def remove_effect(self, effect_type):
            match effect_type:
                case EffectType.SLOW_BALL:
                    self.game.time_scale /= GameConstants.SLOW_FACTOR.value
                case EffectType.HASTE_BALL:
                    self.game.time_scale /= GameConstants.HASTE_FACTOR.value
                case EffectType.ACTIVATE_RESKIN_ON_END:
                    self.toggle_reskin(3)
                case EffectType.PLAY_JULIA_MUSIC_ON_END:
                    self.game.sound_manager.play_music(SfxType.JULIA_MODE_MUSIC)


        def any_of_this_type(self, type):
            for obj in self.game.game_objects:
                if isinstance(obj, type):
                    return True
            return False


        ### OPTIONS ACTIONS ###
        # def toggle_resolution(self): # DEPRECATED
        #     """
        #     Alterna a escala da janela entre 1x, 2x e 3x da resolução base,
        #     mantendo o game space centralizado.
        #     """
        #     current_scale = round(self.game.current_screen_scale())
        #     if current_scale <= 1:
        #         new_scale = 2
        #     elif current_scale == 2:
        #         new_scale = 3
        #     else:
        #         new_scale = 1



        ### INPUTS ###
        def event(self, ev, x, y, st):
            # safeguard contra eventos estranhos
            if not hasattr(ev, "type"):
                print("ERROR: received strange event with no type: ", ev)
                return

            # atualizar posição raw do mouse
            self.game.raw_mouse_x = x
            self.game.raw_mouse_y = y

            # atualizar estado de pressão de teclas
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

            # processar inputs no painel atual
            if self.current_panel is not None:
                self.current_panel.process_inputs(ev)

            if self.should_end_minigame():
                renpy.end_interaction("quit_minigame")
            return None


        ### DEBUG ###
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
            print("LISTING ALL FILES IN THE GAME FOLDER!!!")
            print("")
            list_of_files = renpy.list_files()
            for file in list_of_files:
                print("file: ", file)
            print("total files: ", len(list_of_files))


    class _LayerAsDisplayable(renpy.Displayable):
        """Displayable que devolve um Render (a layer) para poder aplicar Transform(alpha=...)."""
        def __init__(self, get_layer, **kwargs):
            super(_LayerAsDisplayable, self).__init__(**kwargs)
            self.get_layer = get_layer
        def render(self, width, height, st, at):
            return self.get_layer()

