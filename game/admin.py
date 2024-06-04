from django.contrib import admin


from game.models import Game
from game.models import Player
from game.models import Image


class GameAdmin(admin.ModelAdmin):
    list_display = ('code', 'state', 'current_player', 'current_round', 'state', 'round_state', 'display_image')
    list_filter = ('state',)


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'game')


class ImageAdmin(admin.ModelAdmin):
    list_display = ('game', 'player', 'status', 'round', 'external_id', 'prompt', 'selection')


admin.site.register(Game, GameAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Image, ImageAdmin)
