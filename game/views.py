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
    return render(request, 'play.html', context=context)


def index(request):
    return HttpResponse("Hello, world. You're at the game index.")
