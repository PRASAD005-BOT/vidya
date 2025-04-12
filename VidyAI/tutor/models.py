from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import UserProfile, Subject

# Create your models here.
class AIChat(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='chats')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, default=_('Untitled Chat'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.title}"

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('user', _('User')),
        ('ai', _('AI')),
    ]
    
    chat = models.ForeignKey(AIChat, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    language = models.CharField(max_length=5, default='en')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type} message in {self.chat.title}"

class Lesson(models.Model):
    DIFFICULTY_LEVELS = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, default='beginner')
    grade = models.CharField(max_length=2)
    estimated_duration = models.IntegerField(default=20)  # Duration in minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.subject.name} - Grade {self.grade}"

class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    grade = models.CharField(max_length=2, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    time_limit = models.IntegerField(default=30)  # Time limit in minutes
    passing_score = models.IntegerField(default=70)  # Passing score percentage
    
    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', _('Multiple Choice')),
        ('true_false', _('True/False')),
        ('short_answer', _('Short Answer')),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    explanation = models.TextField(blank=True)
    
    def __str__(self):
        return self.question_text[:50]

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.choice_text

class UserLessonProgress(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    progress_percentage = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'lesson')
    
    def __str__(self):
        return f"{self.user.user.username} - {self.lesson.title} - {self.progress_percentage}%"

class UserQuizAttempt(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    date_attempted = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.user.username} - {self.quiz.title} - Score: {self.score}/{self.max_score}"
