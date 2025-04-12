from django.urls import path
from . import views
from . import api

app_name = 'learning'

urlpatterns = [
    path('', views.learning_home, name='learning_home'),
    path('activities/', views.activities, name='activities'),
    path('games/', views.learning_games, name='learning_games'),
    path('progress/', views.learning_progress, name='learning_progress'),
    path('badges/', views.badges, name='badges'),
    path('assessment/', views.assessment, name='assessment'),
    path('learning-style/', views.learning_style_assessment, name='learning_style'),
    path('skill-heatmap/', views.skill_heatmap, name='skill_heatmap'),
    path('badges-showcase/', views.badges_showcase, name='badges_showcase'),
    path('streak-stats/', views.streak_stats, name='streak_stats'),
    path('learning-stats/', views.learning_stats, name='learning_stats'),
    path('learning-history/', views.learning_stats, name='learning_history'),  # Alias for learning stats
    path('skill-assessment/', views.assessment, name='skill_assessment'),  # Alias for assessment
    path('learning-goals/', views.learning_stats, name='learning_goals'),  # Temporary redirect to stats
    path('leaderboard/', views.learning_stats, name='leaderboard'),  # Temporary redirect to stats
    
    # API endpoints
    path('api/track-game-progress/', api.track_game_progress, name='api_track_game_progress'),
    path('api/update-skills/', api.update_skills, name='api_update_skills'),
]

# Additional API routes directly accessible via /api/ prefix
api_patterns = [
    path('learning/track-game-progress/', api.track_game_progress),
    path('learning/update-skills/', api.update_skills),
]