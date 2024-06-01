from django.test import TestCase


from game.models import Game
from game.models import Image
from game.models import Player


class TestGameCreation(TestCase):
    def test_create_game(self):
        # Create the game
        game = Game(code='1234')
        Player(name='Zac', game=game)
        self.assertFalse(game.has_sufficient_players())
        self.assertEqual(game.state, Game.State.WAITING)
        self.assertFalse(game.has_started())

        # Add a second player
        Player(name='Sarah', game=game)
        self.assertTrue(game.has_sufficient_players())
        self.assertEqual(game.state, Game.State.WAITING)
        self.assertFalse(game.has_started())

        # Start the game
        game.start()
        self.assertTrue(game.has_started())
        self.assertEqual(game.state, Game.State.PLAYING)

    def test_create_game_with_incorrect_code(self):
        # Create a game with an incorrect code
        with self.assertRaises(ValueError):
            Game(code='123')

    def test_create_multiple_games_always_has_different_codes(self):
        with self.assertRaises(ValueError):
            g1 = Game(code='1234')
            g1.save()
            Game(code='1234')

    def test_no_two_players_with_same_name(self):
        game = Game(code='1234')
        Player(name='Zac', game=game)

        with self.assertRaises(ValueError):
            Player(name='Zac', game=game)


class TestPlayerCreation(TestCase):
    def test_create_player(self):
        # Create a player
        game = Game(code='1234')
        player = Player(name='Zac', game=game)
        self.assertEqual(player.name, 'Zac')
        self.assertEqual(player.score, 0)

    def test_create_player_with_empty_name(self):
        # Create a player with an empty name
        game = Game(code='1234')
        with self.assertRaises(ValueError):
            Player(name='', game=game)

    def test_create_player_with_name_too_long(self):
        # Create a player with a name that is too long
        with self.assertRaises(ValueError):
            Player(name='a' * 100)


class TestGamePlay(TestCase):
    def test_one_round(self):
        game = Game(code='1234')
        p1 = Player(name='Zac', game=game)
        p2 = Player(name='Sarah', game=game)
        p3 = Player(name='Mark', game=game)
        game.start()

        self.assertEqual(game.current_round, 1)
        game.set_current_player(p1)
        self.assertEqual(game.round_state, Game.RoundState.PROMPT)

        game.play_prompt(p1, 'Dogs playing poker.')
        self.assertEqual(Image.objects.count(), 1)
        image = Image.objects.first()
        self.assertEqual(image.prompt, 'Dogs playing poker.')
        self.assertEqual(game.round_state, Game.RoundState.IMAGE_GENERATION)
        game.game_loop()
        game.game_loop()
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)
        game.play_guess(p2, 'Dogs playing cards.')
        game.game_loop()
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)
        game.play_guess(p3, 'Animals playing cards.')
        game.game_loop()
        game.game_loop()
        self.assertEqual(game.round_state, Game.RoundState.VOTING)
        """
        game.select_image_version(p1, 0)
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)
        game.game_loop()
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)
        game.select_image_version(p2, 0)
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)
        game.select_image_version(p3, 0)
        """
        self.assertEqual(game.round_state, Game.RoundState.VOTING)
        game.game_loop()
        self.assertEqual(game.round_state, Game.RoundState.VOTING)
        game.play_vote(p1, p2)
        self.assertEqual(game.round_state, Game.RoundState.VOTING)
        game.play_vote(p2, p3)
        game.play_vote(p3, p3)

        self.assertEqual(p1.score, 0)
        self.assertEqual(p2.score, 1)
        self.assertEqual(p3.score, 2)

    def test_only_current_player_can_play_prompt(self):
        game = Game(code='1234')
        p1 = Player(name='Zac', game=game)
        p2 = Player(name='Sarah', game=game)
        game.start()
        game.set_current_player(p1)

        with self.assertRaises(ValueError):
            game.play_prompt(p2, 'Dogs playing poker.')


class TestImageGeneration(TestCase):
    def test_generate_image(self):
        g = Game(code='1234')
        g.save()
        p = Player(name='Zac', game=g)
        p.save()
        image = Image(prompt='Dogs playing poker.', game=g, player=p, round=0)
        self.assertEqual(image.status, Image.Status.NOT_STARTED)
        image.generate()
        self.assertEqual(image.status, Image.Status.PENDING)
        image.check_completed()
        self.assertEqual(image.status, Image.Status.COMPLETED)
