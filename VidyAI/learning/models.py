from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import UserProfile, Subject
from django.contrib.auth.models import User
from django.utils import timezone
import json

# Create your models here.
class LearningGame(models.Model):
    GAME_TYPE_CHOICES = [
        ('quiz', _('Quiz Game')),
        ('puzzle', _('Puzzle')),
        ('memory', _('Memory Game')),
        ('matching', _('Matching Game')),
        ('interactive', _('Interactive Story')),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='games')
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES)
    thumbnail = models.ImageField(upload_to='games/', null=True, blank=True)
    min_age = models.PositiveIntegerField(default=5)
    max_age = models.PositiveIntegerField(default=18)
    points_reward = models.PositiveIntegerField(default=10)
    
    def _str_(self):
        return f"{self.name} - {self.game_type}"

class LearningActivity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('video', _('Video')),
        ('reading', _('Reading')),
        ('exercise', _('Exercise')),
        ('project', _('Project')),
        ('experiment', _('Experiment')),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES)
    content = models.TextField(blank=True)
    media_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=15)
    points_reward = models.PositiveIntegerField(default=5)
    
    def _str_(self):
        return f"{self.title} - {self.activity_type}"

class LearningStyleAssessment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='style_assessments')
    visual_score = models.PositiveIntegerField(default=0)
    auditory_score = models.PositiveIntegerField(default=0)
    kinesthetic_score = models.PositiveIntegerField(default=0)
    assessment_date = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    def _str_(self):
        return f"{self.user.user.username}'s Learning Style Assessment"
    
    def get_dominant_style(self):
        scores = {
            'visual': self.visual_score,
            'auditory': self.auditory_score,
            'kinesthetic': self.kinesthetic_score,
        }
        return max(scores, key=scores.get)

class LearningStyle(models.Model):
    """User's learning style preferences"""
    STYLE_CHOICES = [
        ('visual', _('Visual')),
        ('auditory', _('Auditory')),
        ('kinesthetic', _('Kinesthetic')),
    ]
    
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='user_learning_style')
    style = models.CharField(max_length=15, choices=STYLE_CHOICES, default='visual')
    visual_score = models.PositiveIntegerField(default=0)
    auditory_score = models.PositiveIntegerField(default=0)
    kinesthetic_score = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    def _str_(self):
        return f"{self.user.user.username}'s Learning Style: {self.get_style_display()}"
        
    def get_dominant_style(self):
        scores = {
            'visual': self.visual_score,
            'auditory': self.auditory_score,
            'kinesthetic': self.kinesthetic_score,
        }
        return max(scores, key=scores.get)

class EmotionTracking(models.Model):
    EMOTION_CHOICES = [
        ('engaged', _('Engaged')),
        ('confused', _('Confused')),
        ('bored', _('Bored')),
        ('frustrated', _('Frustrated')),
        ('happy', _('Happy')),
        ('tired', _('Tired')),
    ]
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='emotion_data')
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=50, blank=True)
    
    def _str_(self):
        return f"{self.user.user.username} - {self.emotion} - {self.timestamp}"

class UserGameProgress(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='game_progress')
    game = models.ForeignKey(LearningGame, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    highest_level = models.PositiveIntegerField(default=1)
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    time_played_seconds = models.PositiveIntegerField(default=0)
    last_played = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'game')
    
    def _str_(self):
        return f"{self.user.user.username} - {self.game.name} - Level {self.highest_level}"

class UserActivityCompletion(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='completed_activities')
    activity = models.ForeignKey(LearningActivity, on_delete=models.CASCADE)
    completion_date = models.DateTimeField(auto_now_add=True)
    time_spent_minutes = models.PositiveIntegerField(default=0)
    feedback = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('user', 'activity')
    
    def _str_(self):
        return f"{self.user.user.username} - {self.activity.title}"

class SkillCategory(models.Model):
    """Categories for different skill types"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default="fas fa-brain")
    color = models.CharField(max_length=20, default="#4361ee")
    
    def _str_(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Skill Categories"

class Skill(models.Model):
    """Individual skills that can be tracked"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    max_level = models.IntegerField(default=10)
    icon = models.CharField(max_length=50, default="fas fa-star")
    
    def _str_(self):
        return self.name

class Badge(models.Model):
    """Digital badges awarded for achievements"""
    BADGE_LEVELS = (
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    level = models.CharField(max_length=10, choices=BADGE_LEVELS, default='bronze')
    icon = models.CharField(max_length=50, default="fas fa-medal")
    skill = models.ForeignKey(Skill, on_delete=models.SET_NULL, null=True, blank=True, related_name='badges')
    points = models.IntegerField(default=100)
    requirements = models.TextField(help_text="JSON formatted requirements to earn this badge")
    
    def _str_(self):
        return f"{self.get_level_display()} {self.name}"
    
    def get_requirements_dict(self):
        """Returns the requirements as a Python dict"""
        try:
            return json.loads(self.requirements)
        except:
            return {}

class MicroCertification(models.Model):
    """Certifications for completing specific skill paths"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    skills = models.ManyToManyField(Skill, related_name='certifications')
    icon = models.CharField(max_length=50, default="fas fa-certificate")
    required_badges = models.ManyToManyField(Badge, related_name='certifications', blank=True)
    points = models.IntegerField(default=500)
    
    def _str_(self):
        return self.name

class UserSkill(models.Model):
    """Tracks a user's progress in a specific skill"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    current_level = models.IntegerField(default=1)
    progress_to_next = models.FloatField(default=0.0)  # 0.0 to 1.0 for progress bar
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'skill')
    
    def _str_(self):
        return f"{self.user.username}'s {self.skill.name} ({self.current_level})"
    
    def increase_progress(self, amount):
        """Increase skill progress and level up if necessary"""
        self.progress_to_next += amount
        if self.progress_to_next >= 1.0:
            self.level_up()
        self.save()
    
    def level_up(self):
        """Level up this skill"""
        if self.current_level < self.skill.max_level:
            self.current_level += 1
            self.progress_to_next = 0.0
            # Check for badge eligibility
            from learning.services import check_badge_eligibility
            check_badge_eligibility(self.user, self.skill)

class UserBadge(models.Model):
    """Tracks badges earned by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge')
    
    def _str_(self):
        return f"{self.user.username} earned {self.badge.name}"

class UserCertification(models.Model):
    """Tracks certifications earned by users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certifications')
    certification = models.ForeignKey(MicroCertification, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'certification')
    
    def _str_(self):
        return f"{self.user.username} earned {self.certification.name}"

class UserStreak(models.Model):
    """Tracks a user's learning streak"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    def _str_(self):
        return f"{self.user.username}'s streak: {self.current_streak} days"
    
    def update_streak(self):
        """Update the streak based on activity"""
        today = timezone.now().date()
        
        # If first activity, initialize
        if not self.last_activity_date:
            self.current_streak = 1
            self.longest_streak = 1
            self.last_activity_date = today
            self.save()
            return
        
        # If already logged in today, nothing to update
        if self.last_activity_date == today:
            return
            
        # If consecutive day, increase streak
        if (today - self.last_activity_date).days == 1:
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        # If more than one day passed, reset streak
        elif (today - self.last_activity_date).days > 1:
            self.current_streak = 1
        
        self.last_activity_date = today
        self.save()

class GamificationSettings(models.Model):
    """Global settings for gamification"""
    daily_streak_bonus = models.IntegerField(default=10)
    weekly_streak_bonus = models.IntegerField(default=50)
    monthly_streak_bonus = models.IntegerField(default=200)
    
    # Singleton model
    def save(self, *args, **kwargs):
        if self._class_.objects.count():
            self.pk = self._class_.objects.first().pk
        super().save(*args, **kwargs)
    
    def _str_(self):
        return "Gamification Settings"
    
    class Meta:
        verbose_name_plural = "Gamification Settings"

class UserActivity(models.Model):
    """Records various learning activities for gamification"""
    ACTIVITY_TYPES = (
        ('course_progress', 'Course Progress'),
        ('quiz_completion', 'Quiz Completion'),
        ('challenge_win', 'Challenge Win'),
        ('practice_session', 'Practice Session'),
        ('content_creation', 'Content Creation'),
        ('help_others', 'Helping Others'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    points_earned = models.IntegerField()
    skills_affected = models.ManyToManyField(Skill, related_name='activities', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def _str_(self):
        return f"{self.user.username}: {self.description} ({self.points_earned} pts)"
    
    class Meta:
        verbose_name_plural = "User Activities"
        ordering = ['-timestamp']