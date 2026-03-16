define julia = Character(name="Julia", image=None, color="#C161D4")
image bg_julia = "vn_images/ep2 fri_game_julia_likeit2.webp"

init -2 python:
    from constants import GameConstants

transform zoom_4:
    zoom 4
    nearest True


screen ball_minigame(controller):
    modal True

    frame:
        background Solid("#000")
        xalign 0.5
        yalign 0.5
        xsize GameConstants.WIDTH.value * 4
        ysize GameConstants.HEIGHT.value * 4

        add controller xsize GameConstants.WIDTH.value ysize GameConstants.HEIGHT.value at zoom_4, truecenter

        #crie um Displayable muito simples de texto que escreva "Minigame" no centro da tela
        # text "Vector" xalign 0.5 yalign 0.5 size 40 color "#fff"

label start:
    # desativa a tradução automática (força inglês)
    define config.language = "english"
    # desativa o modo de desenvolvedor
    define config.developer = False

    scene bg_julia

    jump minigame
    julia "Hey, let's play a game!"
    menu:
        julia "What do you want to do?"
        "Play minigame":
            jump minigame
        "Exit":
            jump end

label minigame:
    julia "Minigame start!"

    $ quick_menu = False
    $ _game_menu_screen = None
    $ renpy.block_rollback()
    $ config.keymap["director"] = []

    call screen ball_minigame(GameController(1, 3))

    $ quick_menu = True
    $ _game_menu_screen = 'save'
    $ renpy.checkpoint()

    julia "Minigame is over!! Thanks for playing!"
    # jump start

label end:
    # julia "See you later!"
    return
