import time
from game.models import Game

while True:
    games = Game.objects.filter(state='PLAYING')
    for game in games:
        print(game)
        game.game_loop()
        time.sleep(1)
