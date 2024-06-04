from django.db.utils import IntegrityError
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from game.models import Game
from game.models import Image
from game.models import Player


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_game(self):
        response = self.client.post(reverse('create_game'))
        self.assertIsNotNone(response.data.get('game_code'))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Game.objects.count(), 1)

    def test_create_player(self):
        game = Game(code='1234')
        game.save()
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Zac'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Player.objects.count(), 1)

    def test_create_two_players_with_same_name(self):
        game = Game(code='1234')
        game.save()
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Zac'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(Player.objects.count(), 1)
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Zac'})
        self.assertEqual(response.status_code, 400)

    def test_lets_go(self):
        game = Game(code='1234')
        game.save()
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Sarah'})
        response = self.client.post(reverse('lets_go'), {'game_code': '1234', 'name': 'Zac'})
        self.assertEqual(response.status_code, 200)

        game.refresh_from_db()
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(Player.objects.count(), 2)
        self.assertEqual(game.state, Game.State.PLAYING)

    def test_submit_prompt(self):
        game = Game(code='1234')
        game.save()
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Sarah'})
        response = self.client.post(reverse('lets_go'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(
            reverse('submit_prompt'),
            {'game_code': '1234', 'name': 'Zac', 'prompt': 'Dogs playing poker.'}
        )
        self.assertEqual(response.status_code, 200)

        game.refresh_from_db()
        self.assertEqual(Image.objects.count(), 1)
        self.assertEqual(game.round_state, Game.RoundState.IMAGE_GENERATION)

    def test_submit_guess(self):
        game = Game(code='1234')
        game.save()
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Sarah'})
        response = self.client.post(reverse('lets_go'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(
            reverse('submit_prompt'),
            {'game_code': '1234', 'name': 'Zac', 'prompt': 'Dogs playing poker.'}
        )
        game.refresh_from_db()
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        response = self.client.post(
            reverse('submit_guess'),
            {'game_code': '1234', 'name': 'Sarah', 'guess': 'Dogs playing cards.'}
        )
        self.assertEqual(response.status_code, 200)

        game.refresh_from_db()
        self.assertEqual(Image.objects.count(), 2)
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)

    def test_enter_presenting_state(self):
        game = Game(code='1234')
        game.save()
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Sarah'})
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Mark'})
        response = self.client.post(reverse('lets_go'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(
            reverse('submit_prompt'),
            {'game_code': '1234', 'name': 'Zac', 'prompt': 'Dogs playing poker.'}
        )
        game.refresh_from_db()
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        response = self.client.post(
            reverse('submit_guess'),
            {'game_code': '1234', 'name': 'Sarah', 'guess': 'Dogs playing cards.'}
        )
        response = self.client.post(
            reverse('submit_guess'),
            {'game_code': '1234', 'name': 'Mark', 'guess': 'Animals playing cards.'}
        )
        self.assertEqual(response.status_code, 200)
        game.refresh_from_db()
        game.game_loop()
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        self.assertEqual(game.round_state, Game.RoundState.PRESENTING)

    def test_next_round(self):
        game = Game(code='1234')
        game.save()
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Sarah'})
        response = self.client.post(reverse('lets_go'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(
            reverse('submit_prompt'),
            {'game_code': '1234', 'name': 'Zac', 'prompt': 'Dogs playing poker.'}
        )
        game.refresh_from_db()
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        response = self.client.post(
            reverse('submit_guess'),
            {'game_code': '1234', 'name': 'Sarah', 'guess': 'Dogs playing cards.'}
        )
        response = self.client.post(
            reverse('submit_guess'),
            {'game_code': '1234', 'name': 'Sarah', 'guess': 'Dogs playing cards.'}
        )
        self.assertEqual(response.status_code, 200)
        game.refresh_from_db()
        game.game_loop()
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        response = self.client.post(
            reverse('next_round'),
            {'game_code': '1234', 'name': 'Zac'},
        )
        game.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(game.display_image)
        self.assertEqual(game.round_state, Game.RoundState.PROMPT)
        self.assertEqual(game.current_round, 2)
        self.assertEqual(game.current_player, Player.objects.get(name='Sarah'))

    def test_change_display_image(self):
        game = Game(code='1234')
        game.save()
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Sarah'})
        response = self.client.post(reverse('join_game'), {'game_code': '1234', 'name': 'Mark'})
        response = self.client.post(reverse('lets_go'), {'game_code': '1234', 'name': 'Zac'})
        response = self.client.post(
            reverse('submit_prompt'),
            {'game_code': '1234', 'name': 'Zac', 'prompt': 'Dogs playing poker.'}
        )
        game.refresh_from_db()
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        response = self.client.post(
            reverse('submit_guess'),
            {'game_code': '1234', 'name': 'Sarah', 'guess': 'Dogs playing cards.'}
        )
        response = self.client.post(
            reverse('submit_guess'),
            {'game_code': '1234', 'name': 'Mark', 'guess': 'Animals playing cards.'}
        )
        self.assertEqual(response.status_code, 200)
        game.refresh_from_db()
        game.game_loop()
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        self.assertEqual(game.round_state, Game.RoundState.PRESENTING)
        response = self.client.post(
            reverse('change_display_image'),
            {'game_code': '1234', 'name': 'Zac', 'image_id': 1},
        )
        self.assertEqual(response.status_code, 200)
        game.refresh_from_db()
        self.assertEqual(game.display_image, Image.objects.get(id=1))


class TestGameCreation(TestCase):
    def test_full_state(self):
        game = Game(code='1234')
        game.save()
        p1 = Player(name='Zac', game=game)
        p2 = Player(name='Sarah', game=game)
        p1.save()
        p2.save()
        game.set_current_player(p1)
        game.start()
        full_state = game.full_state()
        self.assertEqual(full_state.get('code'), '1234')
        self.assertEqual(full_state.get('state'), 'PLAYING')
        self.assertEqual(full_state.get('round_state'), 'PROMPT')
        self.assertEqual(full_state.get('current_round'), 1)
        self.assertEqual(full_state.get('current_player'), 'Zac')
        self.assertEqual(full_state.get('players'), ['Zac', 'Sarah'])
        self.assertEqual(full_state.get('images'), [])
        self.assertEqual(full_state.get('has_sufficient_players'), True)

        game.play_prompt(p1, 'Dogs playing poker.')
        game.game_loop()
        game.refresh_from_db()
        image = game.full_state().get('images')[0]
        self.assertEqual(image.get('player'), 'Zac')
        self.assertEqual(image.get('prompt'), 'Dogs playing poker.')
        self.assertEqual(image.get('status'), 'PENDING')
        self.assertEqual(image.get('round'), 1)
        game.game_loop()
        game.refresh_from_db()
        self.assertEqual(game.full_state().get('round_state'), 'GUESSING')
        image = game.full_state().get('images')[0]
        self.assertEqual(image.get('status'), 'COMPLETED')

    def test_create_game_random_code(self):
        # Create a game with a random code
        game = Game()
        self.assertIsNotNone(game.code)
        self.assertEqual(len(game.code), 4)

    def test_game_has_url(self):
        # Create a game
        game = Game(code='1234')
        self.assertEqual(game.url(), '/game/1234')

    def test_create_game(self):
        # Create the game
        game = Game(code='1234')
        game.save()
        p1 = Player(name='Zac', game=game)
        p1.save()
        self.assertFalse(game.has_sufficient_players())
        self.assertEqual(game.state, Game.State.WAITING)
        self.assertFalse(game.has_started())

        # Add a second player
        p2 = Player(name='Sarah', game=game)
        p2.save()
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

    def test_get_players(self):
        game = Game(code='1234')
        game.save()
        p1 = Player(name='Zac', game=game)
        p2 = Player(name='Sarah', game=game)
        p1.save()
        p2.save()
        self.assertEqual(list(game.get_players()), [p1, p2])

    def test_create_multiple_games_always_has_different_codes(self):
        with self.assertRaises(IntegrityError):
            g1 = Game(code='1234')
            g1.save()
            g2 = Game(code='1234')
            g2.save()

    def test_no_two_players_with_same_name(self):
        game = Game(code='1234')
        game.save()
        p1 = Player(name='Zac', game=game)
        p1.save()

        with self.assertRaises(IntegrityError):
            p2 = Player(name='Zac', game=game)
            p2.save()


class TestPlayerCreation(TestCase):
    def test_create_player(self):
        # Create a player
        game = Game(code='1234')
        player = Player(name='Zac', game=game)
        self.assertEqual(player.name, 'Zac')

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
    def test_game_loop_doesnt_advance_too_far(self):
        game = Game(code='1234')
        game.save()
        p1 = Player(name='Zac', game=game)
        p2 = Player(name='Sarah', game=game)
        p1.save()
        p2.save()
        game.start()
        self.assertEqual(game.round_state, Game.RoundState.PROMPT)
        game.set_current_player(p1)
        game.play_prompt(p1, 'Dogs playing poker.')
        self.assertEqual(game.round_state, Game.RoundState.IMAGE_GENERATION)
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)
        game.game_loop()
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)

    def test_one_round(self):
        game = Game(code='1234')
        game.save()
        p1 = Player(name='Zac', game=game)
        p2 = Player(name='Sarah', game=game)
        p3 = Player(name='Mark', game=game)
        p1.save()
        p2.save()
        p3.save()
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
        game.refresh_from_db()
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)
        game.play_guess(p2, 'Dogs playing cards.')
        game.game_loop()
        game.refresh_from_db()
        self.assertEqual(game.round_state, Game.RoundState.GUESSING)
        game.play_guess(p3, 'Animals playing cards.')
        game.game_loop()
        game.game_loop()
        game.refresh_from_db()
        self.assertEqual(game.round_state, Game.RoundState.PRESENTING)

        game.next_round()
        self.assertEqual(game.round_state, Game.RoundState.PROMPT)
        self.assertEqual(game.state, Game.State.PLAYING)
        self.assertEqual(game.current_player, p2)

    def test_only_current_player_can_play_prompt(self):
        game = Game(code='1234')
        p1 = Player(name='Zac', game=game)
        p2 = Player(name='Sarah', game=game)
        game.save()
        p1.save()
        p2.save()
        game.start()
        game.set_current_player(p1)

        with self.assertRaises(ValueError):
            game.play_prompt(p2, 'Dogs playing poker.')


class TestImageGeneration(TestCase):
    def test_is_done(self):
        g = Game(code='1234')
        g.save()
        p = Player(name='Zac', game=g)
        p.save()
        image = Image(prompt='Dogs playing poker.', game=g, player=p, round=0)
        self.assertFalse(image.is_done())
        image.generate()
        self.assertFalse(image.is_done())
        image.check_completed()
        self.assertTrue(image.is_done())

    def test_generate_image(self):
        g = Game(code='1234')
        g.save()
        p = Player(name='Zac', game=g)
        p.save()
        image = Image(prompt='Dogs playing poker.', game=g, player=p, round=0)
        self.assertEqual(image.status, Image.Status.NOT_STARTED)
        image.generate()
        self.assertIsNotNone(image.external_id)
        self.assertEqual(image.status, Image.Status.PENDING)
        image.check_completed()
        self.assertIsNotNone(image.selection)
        self.assertEqual(image.status, Image.Status.COMPLETED)
