from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from game.models import Game


@shared_task
def game_loop_task():
    games = Game.objects.filter(
        state='PLAYING',
        created_at__gte=timezone.now() - timedelta(hours=12)
    )
    for game in games:
        game.game_loop()
