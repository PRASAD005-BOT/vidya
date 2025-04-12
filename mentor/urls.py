from django.urls import path
from . import views

app_name = 'mentor'

urlpatterns = [
    path('', views.mentor_home, name='mentor_home'),
    path('find/', views.find_mentor, name='find_mentor'),
    path('register/', views.register_as_mentor, name='register_as_mentor'),
    path('dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('sessions/', views.mentor_sessions, name='mentor_sessions'),
    path('connect/<int:mentor_id>/', views.connect_with_mentor, name='connect_with_mentor'),
] 