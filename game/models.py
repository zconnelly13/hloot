import os
import base64
from datetime import timedelta
import http.client
import json
import random
import uuid

from django.conf import settings
from django.db import models
from django.db import transaction
from django.utils import timezone


class Game(models.Model):

    class State(models.TextChoices):
        WAITING = 'WAITING'
        PLAYING = 'PLAYING'

    class RoundState(models.TextChoices):
        PROMPT = 'PROMPT'
        IMAGE_GENERATION = 'IMAGE_GENERATION'
        GUESSING = 'GUESSING'
        PRESENTING = 'PRESENTING'

    created_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=4, unique=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.WAITING)
    current_player = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='current_player',
    )
    round_state = models.CharField(max_length=20, choices=RoundState.choices, default=RoundState.PROMPT)
    current_round = models.IntegerField(default=1)
    display_image = models.ForeignKey(
        'Image',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='display_image',
    )

    def __str__(self):
        return f'Game {self.code}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.code:
            self.code = str(random.randint(1000, 9999))
        if len(self.code) != 4:
            raise ValueError('Game code must be 4 characters long.')
        if not self.code.isdigit():
            raise ValueError('Game code must be a number.')

    def change_display_image(self, image_id):
        image = Image.objects.get(id=image_id)
        self.display_image = image
        self.save()

    def full_state(self):
        full_state = {}
        full_state['code'] = self.code
        full_state['state'] = self.state
        full_state['round_state'] = self.round_state
        full_state['current_round'] = self.current_round
        full_state['current_player'] = self.current_player.name if self.current_player else None
        full_state['players'] = [player.name for player in self.get_players()]
        full_state['images'] = [image.to_dict() for image in Image.objects.filter(game=self)]
        full_state['has_sufficient_players'] = self.has_sufficient_players()
        full_state['display_image'] = self.display_image.to_dict() if self.display_image else None
        return full_state

    def game_loop(self):
        images = Image.objects.filter(
            game=self,
            round=self.current_round,
            status__in=[Image.Status.NOT_STARTED, Image.Status.PENDING],
        )

        for image in images:
            image.process()

        done_images = Image.objects.filter(
            game=self,
            round=self.current_round,
            status__in=[Image.Status.COMPLETED, Image.Status.ERROR],
        )

        if self.round_state == Game.RoundState.IMAGE_GENERATION and len(done_images) == 1:
            try:
                with transaction.atomic():
                    game = Game.objects.get(id=self.id, round_state=Game.RoundState.IMAGE_GENERATION)
                    game.round_state = Game.RoundState.GUESSING
                    game.save()
            except Game.DoesNotExist:
                pass
        elif self.round_state == Game.RoundState.GUESSING and len(done_images) == self.player_count():
            try:
                with transaction.atomic():
                    game = Game.objects.get(id=self.id, round_state=Game.RoundState.GUESSING)
                    game.round_state = Game.RoundState.PRESENTING
                    game.save()
            except Game.DoesNotExist:
                pass

    def play_prompt(self, player, prompt):
        if self.state != Game.State.PLAYING:
            raise ValueError('Game is not currently playing.')
        if player != self.current_player:
            raise ValueError('It is not this player\'s turn.')

        image, created = Image.objects.get_or_create(prompt=prompt, game=self, player=player, round=self.current_round)
        if created:
            self.round_state = Game.RoundState.IMAGE_GENERATION
            self.save()

    def play_guess(self, player, guess):
        if self.state != Game.State.PLAYING:
            raise ValueError('Game is not currently playing.')
        if self.round_state != Game.RoundState.GUESSING:
            raise ValueError('It is not the guessing phase.')

        image, _ = Image.objects.get_or_create(prompt=guess, game=self, player=player, round=self.current_round)

    def set_current_player(self, player):
        self.current_player = player
        self.save()

    def has_sufficient_players(self):
        return self.player_count() >= 2

    def has_started(self):
        return self.state == Game.State.PLAYING

    def start(self):
        if not self.has_sufficient_players():
            raise ValueError('Not enough players to start the game.')
        self.state = Game.State.PLAYING
        self.round_state = Game.RoundState.PROMPT
        self.save()

    def url(self):
        return f'/game/{self.code}'

    def get_players(self):
        return Player.objects.filter(game=self).order_by('id')

    def player_count(self):
        return Player.objects.filter(game=self).count()

    def next_player(self):
        players = self.get_players()
        players = list(players)
        current_index = players.index(self.current_player)
        next_index = (current_index + 1) % len(players)
        self.current_player = players[next_index]
        self.save()

    def next_round(self):
        self.round_state = Game.RoundState.PROMPT
        self.next_player()
        self.current_round = self.current_round + 1
        self.display_image = None
        self.save()


class Player(models.Model):
    name = models.CharField(max_length=30)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'game')

    def __str__(self):
        return f'Player {self.name}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.name == '':
            raise ValueError('Player name cannot be empty.')

        if len(self.name) > 30:
            raise ValueError('Player name cannot be longer than 30 characters.')


class Image(models.Model):

    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED'
        PENDING = 'PENDING'
        ERROR = 'ERROR'
        COMPLETED = 'COMPLETED'

    created_at = models.DateTimeField(auto_now_add=True)
    prompt = models.CharField(max_length=1024)
    choice1 = models.URLField(null=True, blank=True)
    choice2 = models.URLField(null=True, blank=True)
    choice3 = models.URLField(null=True, blank=True)
    choice4 = models.URLField(null=True, blank=True)
    selection = models.URLField(null=True, blank=True)
    external_id = models.CharField(max_length=1024, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    round = models.IntegerField()
    image_data = models.TextField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'Image {self.prompt}, Status: {self.status}'

    def is_done(self):
        return self.status == Image.Status.COMPLETED

    def to_dict(self):
        return {
            'id': self.id,
            'player': self.player.name,
            'prompt': self.prompt,
            'selection': self.selection,
            'status': self.status,
            'round': self.round,
        }

    def check_timed_out(self):
        if self.created_at < timezone.now() - timedelta(minutes=5):
            self.status = Image.Status.COMPLETED
            self.selection = "https://static.vecteezy.com/system/resources/previews/007/077/420/non_2x/time-out-advertising-badge-sticker-with-clock-icon-time-out-illustration-free-vector.jpg"  # noqa: E501
            self.save()
            return True
        return False

    def process(self):
        if self.status == Image.Status.NOT_STARTED:
            self.generate()
        elif self.status == Image.Status.PENDING:
            self.check_completed()

    def generate(self):
        if self.check_timed_out():
            return
        if settings.TESTING or settings.MIDJOURNEY_API_KEY == 'DEV':
            self.external_id = '1234'
            self.status = Image.Status.PENDING
            self.save()
            return

        # This is also not good to do here it should be done in celery or something
        with transaction.atomic():
            if self.status == Image.Status.NOT_STARTED:
                try:
                    Image.objects.get(id=self.id, status=Image.Status.NOT_STARTED)
                except Image.DoesNotExist:
                    return
                self.status = Image.Status.PENDING
                self.external_id = str(uuid.uuid4())
                self.save()

                data = {
                    "prompt": f"{self.prompt}",
                    "steps": 25,
                    "force_task_id": self.external_id,
                }

                headers = {
                    'Content-Type': 'application/json'
                }

                conn = http.client.HTTPConnection("host.docker.internal", 7860)
                conn.request("POST", "/sdapi/v1/txt2img", body=json.dumps(data), headers=headers)

                response = conn.getresponse()
                response_data = json.loads(response.read().decode('utf-8'))
                print(response_data)
                self.image_data = response_data['images'][0]
                self.save()

    def check_completed(self):
        if self.check_timed_out():
            return

        # Note: Do not do this mock this out properly ffs
        if settings.TESTING or settings.MIDJOURNEY_API_KEY == 'DEV':
            self.selection = f'https://picsum.photos/{str(random.randint(1000, 1050))}'
            self.status = Image.Status.COMPLETED
            self.save()
            return

        with transaction.atomic():
            if self.status == Image.Status.PENDING:
                try:
                    Image.objects.get(id=self.id, status=Image.Status.PENDING)
                except Image.DoesNotExist:
                    return

                if self.image_data is not None:
                    image_dir = os.path.join(settings.MEDIA_ROOT, 'generated_images')
                    os.makedirs(image_dir, exist_ok=True)
                    image_path = os.path.join(image_dir, f'{self.external_id}.png')
                    with open(image_path, 'wb') as f:
                        f.write(base64.b64decode(self.image_data))
                    self.status = Image.Status.COMPLETED
                    self.selection = settings.MEDIA_URL + f'generated_images/{self.external_id}.png'
                    self.save()
