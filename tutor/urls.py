from django.urls import path
from . import views

app_name = 'tutor'

urlpatterns = [
    path('', views.tutor_home, name='tutor_home'),
    path('chat/', views.ai_chat, name='ai_chat'),
    path('generate-content/', views.generate_content, name='generate_content'),
    path('quizzes/', views.quizzes, name='quizzes'),
    path('lessons/', views.lessons, name='lessons'),
    path('subjects/', views.subjects, name='subjects'),
] 