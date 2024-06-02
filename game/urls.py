from django.urls import path

from . import views

urlpatterns = [
    path("create", views.create_game, name="create_game"),
    path("join_game", views.join_game, name="join_game"),
    path("lets_go", views.lets_go, name="lets_go"),
    path("state", views.state, name="state"),
    path("submit_prompt", views.submit_prompt, name="submit_prompt"),
    path("submit_guess", views.submit_guess, name="submit_guess"),
    path("next_round", views.next_round, name="next_round"),
    path("change_display_image", views.change_display_image, name="change_display_image"),
]
