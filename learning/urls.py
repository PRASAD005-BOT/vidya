from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.learning_home, name='learning_home'),
    path('activities/', views.activities, name='activities'),
    path('games/', views.learning_games, name='learning_games'),
    path('progress/', views.learning_progress, name='learning_progress'),
    path('badges/', views.badges, name='badges'),
    path('assessment/', views.assessment, name='assessment'),
    path('learning-style/', views.learning_style_assessment, name='learning_style'),
] 