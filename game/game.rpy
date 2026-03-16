define julia = Character(name="Julia", image=None, color="#C161D4")
define simon = Character(name="Simon", image=None, color="#5995ED")
image bg_julia = "vn_images/ep2 fri_game_julia_likeit2.webp"
image black = "#000"

define happy_song = "songs/nice_morning_loop.mp3"

init -2 python:
    from constants import GameConstants

    def prepare_minigame():
        renpy.store.quick_menu = False
        renpy.store._game_menu_screen = None
        renpy.block_rollback()

    def back_from_minigame():
        renpy.store.quick_menu = True
        renpy.store._game_menu_screen = 'save'
        renpy.checkpoint()

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

    jump story_mode

label story_mode:
    stop music
    scene black
    "Nota do desenvolvedor: este pequeno modo história foi feito usando assets e personagens da OppaiMan com permissão e todo o respeito possível ao material de origem."
    "O intuito é demonstrar algumas possibilidades de integrar a história com o minigame."
    "Obrigado pela oportunidade, espero que gostem!"

    scene black
    simon "Era uma quarta-feira qualquer, eu estava em casa."
    simon "Eu ouço a campainha tocar, e então vejo Julia batendo à minha porta."

    play music happy_song
    scene bg_julia
    play music "songs/nice_morning_loop.mp3"
    julia "Oi Simon, como vai?"
    julia "Você parece um pouco pra baixo. Tá tudo bem?"

    simon "Oi Julia! Eu tô bem, só um pouco cansado. Tô terminando um projeto pra faculdade."

    julia "(Pera, qual era mesmo o curso dele?)"
    julia "É mesmo? Qual é esse trabalho?"
    
    simon "É um joguinho Brick Break. É pra disciplina de criação de jogos."

    julia "Um jogo? Uau, isso é muito legal!!!"
    julia "Posso jogar?"

    simon "Claro, vá em frente."
    simon "Ainda está um pouco cru, mas gostaria de ouvir suas opiniões sobre ele."

    $ prepare_minigame()
    call screen ball_minigame(GameController(1))
    $ back_from_minigame()

    stop music
    play music happy_song
    simon "E então, o que achou?"

    julia "Uau! Eu amei!"
    julia "Mas eu acho que precisa de mais coisas!"

    simon "O que você está pensando?"
    
    julia "Deixa eu ver, deixa eu ver..."
    julia "Ah! Já sei!"

    julia "Talvez a interface poderia melhorar, como a logo principal ou algo assim. E ter mais efeitos visuais também."

    simon "Entendi..."

    julia "E, e..."
    julia "Ah, poderia ter portais, e mais poderes!"

    simon "Portais...?"
    
    julia "Sim!"
    julia "E seria muito legal se a raquete pudesse pular!"
    julia "Você poderia bater na bola pulando para refleti-la de volta mais rápido! Como um golpe bem fortão!"

    simon "A raquete pular...?"

    julia "E, e a bola podia PEGAR FOGO! E derreter os blocos como se fossem manteiga!"
    julia "E, e depois..."

    simon "Err..."

    julia "Você podia fazer tudo mais bonito, tipo um pouco mais colorido e com mais cor-de-rosa!"
    julia "Umas pétalas de cerejeira caindo, oh, seria muito legal!!!"

    simon "Calma..."
    simon "São muitas ideias de uma vez só. Se eu fizer tudo isso, eu jamais vou conseguir terminar o jogo!"

    julia "Desculpa, haha. Acho que eu me empolguei..."
    julia "Mas é porque eu realmente gostei!"

    simon "Que bom! Agradeço muito as sugestões."
    simon "Ainda tenho um tempinho para trabalhar nele. Vamos ver o que eu consigo fazer."

    julia "Certo, mas isso depois! Você precisa tirar um tempinho pra descansar agora! Dar um break!"
    julia "Senta aí, eu vou te fazer uma massagem!"

    simon "Acho que é disso mesmo que eu estou precisando..."

    scene black with fade
    "A tarde passou rápido."
    "Julia falava sem parar, inventando ideias malucas para o jogo."
    "Eu não conseguia parar de rir com as ideias mais mirabolantes."
    "Pela primeira vez em dias, eu esqueci completamente do estresse da faculdade."
    "Acho que tudo que eu precisava mesmo era de uma tarde de relaxamento assim."
    "Alguns dias depois..."

    scene bg_julia with fade
    simon "Oi Julia! Eu terminei o projeto!"
    simon "Eu adicionei algumas das suas sugestões, e está bem mais legal agora!"

    julia "Uau! Deixa eu jogar!"

    $ prepare_minigame()
    call screen ball_minigame(GameController(2))
    $ back_from_minigame()
    
    stop music
    play music happy_song
    julia "Minha nossa, está muito melhor! O pulo deixou bem mais dinâmico!"
    julia "Você é muito talentoso com isso, Simon!"
    julia "Já pensou em fazer jogos como uma carreira?"

    simon "Não, na verdade não. Eu não acho que seja pra tanto."
    simon "Mas fico muito feliz que você gostou!"

    julia "Para a próxima versão a gente podia adicionar mais um monte de coisas, tipo, os portais e..."

    simon "Desculpa, Julia. Eu sei que você está muito animada com isso, mas..."
    simon "Infelizmente não vai ter uma próxima versão."

    julia "Por quê?"

    simon "Eu acho que já trabalhei o bastante nesse projeto. Eu realmente gosto de trabalhar nele, mas..."
    simon "Eu já entreguei ele para meu professor e tenho alguns exames finais difíceis para estudar."

    julia "Awww, é uma pena..."
    julia "Mas fico feliz que seu joguinho tenha ficado tão divertido! Seu professor gostou?"

    simon "Sim, eu tirei um A! Eu tô muito orgulhoso!"

    julia "E é isso que mais importa, né?"
    julia "Posso pelo menos ficar com uma cópia do jogo? Eu adoraria aumentar meu highscore!"

    simon "Claro, jogue o quanto quiser!"

    scene black with fade
    "Alguns dias se passaram..."
    "Eu me concentrei muito nos meus exames finais, e não consegui ver a Julia por um tempo..."
    "Mas depois que os exames acabaram, ela concordou em vir pra minha casa jogar mais jogos comigo!"
    "Talvez não só jogos..."

    scene bg_julia with fade
    simon "Há quanto tempo, Julia!"

    julia "Simon! Eu senti taaaaanta saudade! Que bom que sobreviveu às suas provas finais!"
    julia "Mas hehe, deixa eu te mostrar algo!"
    "Ela tirou um pendrive da sua bolsa e plugou no computador rapidamente."
    "Nem errou o lado do USB, haha."

    simon "Hum, o que é isso? Algum jogo novo?"

    julia "Siiim! Não é apenas 'algum novo jogo'. É O PRÓXIMO GRANDE JOGO!"
    julia "Eu chamo de 'Best Brick Breaker 2.0'!"

    simon "Best Brick Breaker 2.0? Foi você quem..?"

    julia "Vamos, vamos! Vamos jogar!"
    julia "Eu sei que você vai gostar!"

    $ prepare_minigame()
    call screen ball_minigame(GameController(3))
    $ back_from_minigame()

    stop music
    play music happy_song
    simon "Uau, Julia..."
    simon "Isso foi INCRÍVEL!"

    julia "Entãaaao!!! Muito legal, né?"

    simon "Estou muito impressionado! Como você aprendeu a fazer tudo isso?"

    julia "Você me subestima, Simon! Na verdade eu roubei alguns livros do seu quarto para me ajudar!"
    
    simon "Você roubou???"

    julia "Siiim!!! Eles não ajudaram muito, porque eu não entendi nadica de nada!"
    julia "Mas depois eu pedi ajuda para a Riko online, e ela salvou a minha pele!"
    julia "Você sabia que ela tem um tio que trabalha na Nintendo?"

    simon "Uau, você nunca para de me surpreender, Julia. Você é a melhor!"

    julia "Obrigada!"
    julia "Sabe, eu sou super agradecida por tudo que você faz por mim."
    julia "Desde que conheci você, eu comecei a acreditar em mim mais e mais!"
    julia "Então eu sempre penso em formas de te pagar de volta por tudo isso."

    simon "Julia, eu fico até emocionado em ouvir isso!"
    simon "Sabe, na verdade eu fiz esse jogo pra uma disciplina. Eu fiz pra você."
    simon "Meu curso da faculdade não tem nada a ver com games, haha. Não sei como você não desconfiou."
    simon "Me dediquei para aprender a fazer ele porque eu sei que você adora jogos, e queria ver você feliz."

    "Julia morde o lábio inferior."
    julia "Você... fez isso por mim?"

    simon "Tudo que eu faço por você... é porque eu gosto muito, muito mesmo de você."
    simon "Não precisa me 'pagar de volta' por nada."

    "O estômago de Simon ronca, reclamando que ele não come nada há um bom tempo."
    simon "Quero dizer, você sempre pode me pagar um almoço, haha."
    
    julia "Hahaha, um almoço é? Quem sabe mais tarde."
    "Julia olha para Simon com um sorriso safado e começa a tirar as roupas lentamente."
    # julia starts stripping
    julia "Mas agora eu tenho outras coisas em mente..."

    scene black with fade
    "Break Time with Julia!"
    "Desenvolvido por Renan Rodrigues com dedicação para a OppaiMan."
    "Obrigado por jogar!"

    jump end

label arcade_mode:
    $ prepare_minigame()
    call screen ball_minigame(GameController(-1))
    $ back_from_minigame()

label end:
    # julia "See you later!"
    return
