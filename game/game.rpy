define julia = Character("Julia", color="#C161D4")

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
    scene bg room
    show julia happy

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

    call screen ball_minigame(GameController())

    $ quick_menu = True
    $ _game_menu_screen = 'save'
    $ renpy.checkpoint()

    julia "Minigame is over!! Thanks for playing!"
    # jump start

label end:
    julia "See you later!"
    return
