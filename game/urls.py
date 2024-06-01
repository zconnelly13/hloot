from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("host", views.host, name="host"),
    path("<str:code>", views.game, name="game"),
    path("play/<str:code>", views.play, name="play"),
]
