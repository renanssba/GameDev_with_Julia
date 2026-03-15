init -1 python:
    import pygame
    import random
    from constants import GameConstants
    from ball import Ball
    from brick import Brick
    from game_context import GameContext, GameState
    from stage_controller import StageController
    from ui_info_panel import UiInfoPanel
    from ui_gameplay_panel import UiGameplayPanel
    from ui_pause_panel import UiPausePanel
    from ui_title_panel import UiTitlePanel
    from ui_options_panel import UiOptionsPanel
    from ui_leaderboard_panel import UiLeaderboardPanel
    from ui_end_card_panel import UiEndCardPanel
    from sound_manager import SoundManager, SfxType
    from effects import EffectType
    from effect_controller import EffectController
    import renpy.display.im as im
    from renpy.display.core import IgnoreEvent

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

            # Panels first (so they exist even if stage setup fails)
            self.title_ui = UiTitlePanel(self.game)
            self.gameplay_panel = UiGameplayPanel(self.game)
            self.pause_ui = UiPausePanel(self.game)
            self.options_panel = UiOptionsPanel(self.game)
            self.leaderboard_panel = UiLeaderboardPanel(self.game)
            
            # Setup stage (player, sound, level)
            self.stage_controller = StageController(self.game)
            self.stage_controller.setup(self.game.stage_id)

            # Initialize game-wide effects
            self.effect_controller = EffectController(self)

            # End card panels
            self.victory_panel = UiEndCardPanel(self.game.ui_font_bold, ["YOU WIN!", "Score 1000"], self.game)
            self.defeat_panel = UiEndCardPanel(self.game.ui_font_bold, ["GAME OVER", "Try again", "Score 1000"], self.game)

            self.victory_panel.show_panel = (lambda: self.game.sound_manager.play_music(SfxType.VICTORY_MUSIC))
            self.defeat_panel.show_panel = (lambda: self.game.sound_manager.stop_music())

            # DEBUG PRINT ALL FILES
            self.print_list_files()

            # Initialize last frame time
            self.last_st = 0.0

            self.panel_list = []

            # DEBUG
            # self.game.debug = True
            if(self.game.debug):
                self.open_panel(self.gameplay_panel)
            else:
                self.open_panel(self.title_ui)
            # self.open_panel(self.gameplay_panel)


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
            # print("st: ", st, " last_st: ", self.last_st, " delta_time: ", self.game.delta_time)
            self.last_st = st

            self.game._unscaled_frame += 1

            self.game.delta_time = self.game._clock.tick(60) / 1000
            self.game.delta_time = max(0.01, min(0.1, self.game.delta_time))

            if self.effect_controller.has_effect(EffectType.HITSTOP):
                intensity = self.effect_controller.get_effect(EffectType.HITSTOP).intensity
                renpy.redraw(self, intensity / 60.0)
                return
            
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
            else:
                self.game.player.spawn_text_particle(f"+{amount}")

        def update_ui(self):
            self.gameplay_panel.update_ui()

        ### PHYSICS ###
        def apply_physics_to_all(self):
            for obj in self.game.game_objects:
                obj.apply_physics()
            self.effect_controller.update()
            
        
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

            color_game_space = GameConstants.COLOR_GAME_SPACE.value
            color_game_space_border = GameConstants.COLOR_GAME_SPACE_BORDER.value
            color_transparent = GameConstants.COLOR_TRANSPARENT.value
            color_black = GameConstants.COLOR_RAW_BLACK.value
            
            # self.game._background_layer.fill(color_transparent)

            
        def merge_all_layers(self):
            self.game.main_render.blit(self.game._background_layer, (0, 0))
            self.game.main_render.blit(self.game._effects_back_layer, (0, 0))
            self.game.main_render.blit(self.game._foreground_layer, (0, 0))
            self.game.main_render.blit(self.game._effects_front_layer, (0, 0))
            self.game.main_render.blit(self.game._ui_layer, (0, 0))



        ### FLOW AND MISC EFFECTS ###
        def set_game_state(self, game_state):
            self.game.set_state(game_state)
            match game_state:
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
                    self.open_panel(self.title_ui)
                    self.open_panel(self.victory_panel)
                case GameState.DEFEAT:
                    self.close_all_panels()
                    self.open_panel(self.title_ui)
                    self.open_panel(self.defeat_panel)

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

        def is_still_running(self):
            return self.panel_list != []


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


        ### OPTIONS ACTIONS ###
        def toggle_fullscreen(self):
            """Alterna o modo fullscreen da janela usando o display atual (SCALED)."""
            pygame.display.toggle_fullscreen()

        def toggle_resolution(self):
            """
            Alterna a escala da janela entre 1x, 2x e 3x da resolução base,
            mantendo o game space centralizado.
            """
            current_scale = round(self.game.current_screen_scale())
            if current_scale <= 1:
                new_scale = 2
            elif current_scale == 2:
                new_scale = 3
            else:
                new_scale = 1



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

            if not self.is_still_running():
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

