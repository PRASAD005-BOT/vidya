from django.urls import path
from . import views

app_name = 'tutor'

urlpatterns = [
    path('', views.tutor_home, name='tutor_home'),
    path('chat/', views.ai_chat, name='ai_chat'),
    path('generate-content/', views.generate_content_view, name='generate_content'),
    path('quizzes/', views.quizzes, name='quizzes'),
    path('quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quizzes/<int:quiz_id>/fix/', views.fix_empty_quiz, name='fix_empty_quiz'),
    path('quizzes/<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('lessons/', views.lessons, name='lessons'),
    path('lessons/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('subjects/', views.subjects, name='subjects'),
    path('subjects/<int:subject_id>/lessons/', views.subject_lessons, name='subject_lessons'),
    path('subjects/<int:subject_id>/quizzes/', views.subject_quizzes, name='subject_quizzes'),
] 