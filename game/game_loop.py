import time
from datetime import timedelta

from django.utils import timezone

from game.models import Game

while True:
    games = Game.objects.filter(
        state='PLAYING',
        created_at__gte=timezone.now() - timedelta(hours=12)
    )
    for game in games:
        game.game_loop()
    time.sleep(5)
