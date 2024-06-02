from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from game.models import Game
from game.models import Player


def host(request):
    game = Game()
    game.save()
    return redirect(game.url())


def game(request, code):
    game = Game.objects.get(code=code)
    game.save()
    context = {}
    context['code'] = code
    context['players'] = game.get_players()
    context['game'] = game
    return render(request, 'game.html', context=context)


def play(request, code):
    game = Game.objects.get(code=code)
    context = {}
    context['code'] = code
    player, _ = Player.objects.get_or_create(name=request.GET['name'], game=game)
    context['player'] = player
    context['has_sufficient_players'] = game.has_sufficient_players()
    context['game_is_started'] = game.has_started()
    context['is_main_player'] = game.current_player == player
    context['current_player'] = game.current_player.name
    context['game_state'] = game.state
    context['game_round_state'] = game.round_state
    if request.method == 'POST':
        if request.POST.get('type') == "letsgo":
            game.start()
            game.set_current_player(player)
            game.save()
        elif request.POST.get('type') == "submit_text":
            game.play_prompt(player, request.POST['prompt'])
            game.save()
    return render(request, 'play.html', context=context)


def index(request):
    return HttpResponse("Hello, world. You're at the game index.")
