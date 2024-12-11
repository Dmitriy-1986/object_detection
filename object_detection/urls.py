from django.urls import path
from . import views

urlpatterns = [
    path('video_feed/', views.video_feed, name='video_feed'),  # Подача видеопотока
    path('esp32_stream/', views.esp32_stream, name='esp32_stream'),  # HTML страница
]


