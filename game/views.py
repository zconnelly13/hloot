from django.db.utils import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response

from game.models import Game
from game.models import Player


@api_view(['POST'])
def create_game(request):
    game = Game()
    game.save()
    return Response({'game_code': game.code}, status=201)


@api_view(['GET'])
def state(request, code):
    game = Game.objects.get(code=code)
    game.game_loop()
    return Response(game.full_state(), status=200)


@api_view(['POST'])
def join_game(request):
    game = Game.objects.get(code=request.POST.get('game_code'))
    name = request.POST.get('name')
    try:
        player = Player(name=name, game=game)
        player.save()
    except IntegrityError:
        return Response({'error': 'Name already taken'}, status=400)
    return Response(game.full_state(), status=200)


@api_view(['POST'])
def lets_go(request):
    game_code = request.POST.get('game_code')
    player_name = request.POST.get('name')
    game = Game.objects.get(code=game_code)
    game.set_current_player(Player.objects.get(name=player_name, game=game))
    game.start()
    return Response(game.full_state(), status=200)


@api_view(['POST'])
def submit_prompt(request):
    game_code = request.POST.get('game_code')
    player_name = request.POST.get('name')
    prompt = request.POST.get('prompt')
    game = Game.objects.get(code=game_code)
    player = Player.objects.get(name=player_name, game=game)
    game.play_prompt(player, prompt)
    return Response(game.full_state(), status=200)


@api_view(['POST'])
def submit_guess(request):
    game_code = request.POST.get('game_code')
    player_name = request.POST.get('name')
    guess = request.POST.get('guess')
    game = Game.objects.get(code=game_code)
    player = Player.objects.get(name=player_name, game=game)
    game.play_guess(player, guess)
    return Response(game.full_state(), status=200)


@api_view(['POST'])
def next_round(request):
    game_code = request.POST.get('game_code')
    game = Game.objects.get(code=game_code)
    game.next_round()
    return Response(game.full_state(), status=200)


@api_view(['POST'])
def change_display_image(request):
    game_code = request.POST.get('game_code')
    image_id = request.POST.get('image_id')
    game = Game.objects.get(code=game_code)
    game.change_display_image(image_id)
    return Response(game.full_state(), status=200)
