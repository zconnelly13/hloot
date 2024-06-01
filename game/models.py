from django.db import models


class Game(models.Model):

    class State(models.TextChoices):
        WAITING = 'WAITING'
        PLAYING = 'PLAYING'

    class RoundState(models.TextChoices):
        PROMPT = 'PROMPT'
        IMAGE_GENERATION = 'IMAGE_GENERATION'
        GUESSING = 'GUESSING'
        VOTING = 'VOTING'

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

    def __str__(self):
        return f'Game {self.code}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self.code) != 4:
            raise ValueError('Game code must be 4 characters long.')
        if not self.code.isdigit():
            raise ValueError('Game code must be a number.')
        if Game.objects.filter(code=self.code).exists():
            raise ValueError('Game with that code already exists.')
        self.save()

    def game_loop(self):
        images = Image.objects.filter(game=self)
        if len(images) == 0:
            return

        for image in images:
            if image.status == Image.Status.NOT_STARTED:
                image.generate()
            elif image.status == Image.Status.PENDING:
                image.check_completed()

        if all([image.status == Image.Status.COMPLETED for image in images]):
            if self.round_state == Game.RoundState.IMAGE_GENERATION:
                self.round_state = Game.RoundState.GUESSING
            elif self.round_state == Game.RoundState.GUESSING:
                self.round_state = Game.RoundState.VOTING

    def play_vote(self, player, votee):
        if self.state != Game.State.PLAYING:
            raise ValueError('Game is not currently playing.')
        if self.round_state != Game.RoundState.VOTING:
            raise ValueError('It is not the voting phase.')

        votee.score += 1
        votee.save()

    def play_prompt(self, player, prompt):
        if self.state != Game.State.PLAYING:
            raise ValueError('Game is not currently playing.')
        if player != self.current_player:
            raise ValueError('It is not this player\'s turn.')

        Image(prompt=prompt, game=self, player=player, round=self.current_round)
        self.round_state = Game.RoundState.IMAGE_GENERATION
        self.save()

    def play_guess(self, player, guess):
        if self.state != Game.State.PLAYING:
            raise ValueError('Game is not currently playing.')
        if self.round_state != Game.RoundState.GUESSING:
            raise ValueError('It is not the guessing phase.')

        Image(prompt=guess, game=self, player=player, round=self.current_round)
        self.save()

    def set_current_player(self, player):
        self.current_player = player
        self.save()

    def has_sufficient_players(self):
        return self.player_set.count() >= 2

    def has_started(self):
        return self.state == Game.State.PLAYING

    def start(self):
        if not self.has_sufficient_players():
            raise ValueError('Not enough players to start the game.')
        self.state = Game.State.PLAYING
        self.save()


class Player(models.Model):
    name = models.CharField(max_length=30)
    score = models.IntegerField(default=0)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f'Player {self.name}'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.score = 0
        if self.name == '':
            raise ValueError('Player name cannot be empty.')

        if len(self.name) > 30:
            raise ValueError('Player name cannot be longer than 30 characters.')

        if Player.objects.filter(name=self.name, game=self.game).exists():
            raise ValueError('Player with that name already exists in this game.')
        self.save()


class Image(models.Model):

    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED'
        PENDING = 'PENDING'
        ERROR = 'ERROR'
        COMPLETED = 'COMPLETED'

    prompt = models.CharField(max_length=1024)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    round = models.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.save()

    def __str__(self):
        return f'Image {self.url}'

    def generate(self):
        # TODO: Actually call midjourney API
        self.status = Image.Status.PENDING
        self.save()

    def check_completed(self):
        # TODO: Actually call midjourney API
        self.status = Image.Status.COMPLETED
        self.save()
