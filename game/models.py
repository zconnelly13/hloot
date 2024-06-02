import random

from django.db import models


class Game(models.Model):

    class State(models.TextChoices):
        WAITING = 'WAITING'
        PLAYING = 'PLAYING'

    class RoundState(models.TextChoices):
        PROMPT = 'PROMPT'
        IMAGE_GENERATION = 'IMAGE_GENERATION'
        GUESSING = 'GUESSING'
        PRESENTING = 'PRESENTING'

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
        return full_state

    def game_loop(self):
        images = Image.objects.filter(game=self, round=self.current_round)
        if len(images) == 0:
            return

        for image in images:
            image.process()

        if all([image.is_done() for image in images]):
            if self.round_state == Game.RoundState.IMAGE_GENERATION:
                self.round_state = Game.RoundState.GUESSING
            elif self.round_state == Game.RoundState.GUESSING and len(images) > 1:
                self.round_state = Game.RoundState.PRESENTING
        self.save()

    def play_prompt(self, player, prompt):
        if self.state != Game.State.PLAYING:
            raise ValueError('Game is not currently playing.')
        if player != self.current_player:
            raise ValueError('It is not this player\'s turn.')

        image = Image(prompt=prompt, game=self, player=player, round=self.current_round)
        image.save()
        self.round_state = Game.RoundState.IMAGE_GENERATION
        self.save()

    def play_guess(self, player, guess):
        if self.state != Game.State.PLAYING:
            raise ValueError('Game is not currently playing.')
        if self.round_state != Game.RoundState.GUESSING:
            raise ValueError('It is not the guessing phase.')

        image = Image(prompt=guess, game=self, player=player, round=self.current_round)
        image.save()
        self.save()

    def set_current_player(self, player):
        self.current_player = player
        self.save()

    def has_sufficient_players(self):
        return self.get_players().count() >= 2

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
        self.current_round += 1
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f'Image {self.prompt}, Status: {self.status}'

    def is_done(self):
        return self.status == Image.Status.COMPLETED

    def to_dict(self):
        return {
            'player': self.player.name,
            'prompt': self.prompt,
            'selection': self.selection,
            'status': self.status,
            'round': self.round,
        }

    def process(self):
        if self.status == Image.Status.NOT_STARTED:
            self.generate()
        elif self.status == Image.Status.PENDING:
            self.check_completed()

    def generate(self):
        # TODO: Actually call midjourney API
        self.external_id = '1234'

        # Real Code
        self.status = Image.Status.PENDING
        self.save()

    def check_completed(self):
        # TODO: Actually call midjourney API
        self.selection = 'https://picsum.photos/1024'

        # Real Code
        self.status = Image.Status.COMPLETED
        self.save()
