from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Create your models here.
class UserProfile(models.Model):
    LEARNING_STYLE_CHOICES = [
        ('visual', _('Visual Learner')),
        ('auditory', _('Auditory Learner')),
        ('kinesthetic', _('Kinesthetic Learner')),
        ('unknown', _('Not Determined Yet')),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('hi', _('Hindi')),
        ('ta', _('Tamil')),
        ('te', _('Telugu')),
        ('bn', _('Bengali')),
        ('mr', _('Marathi')),
        ('gu', _('Gujarati')),
        ('kn', _('Kannada')),
        ('ml', _('Malayalam')),
        ('pa', _('Punjabi')),
        ('or', _('Odia')),
    ]
    
    GRADE_CHOICES = [
        ('1', _('Grade 1')),
        ('2', _('Grade 2')),
        ('3', _('Grade 3')),
        ('4', _('Grade 4')),
        ('5', _('Grade 5')),
        ('6', _('Grade 6')),
        ('7', _('Grade 7')),
        ('8', _('Grade 8')),
        ('9', _('Grade 9')),
        ('10', _('Grade 10')),
        ('11', _('Grade 11')),
        ('12', _('Grade 12')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLE_CHOICES, default='unknown')
    school_name = models.CharField(max_length=255, blank=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    bpl_card_number = models.CharField(max_length=20, blank=True, help_text=_('Below Poverty Line card number'))
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    points = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_active = models.DateField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='badges/')
    points_required = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'badge')
        
    def __str__(self):
        return f"{self.user.user.username} - {self.badge.name}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='subjects/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class UserProgress(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='progress')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    proficiency_level = models.IntegerField(default=1)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'subject')
        
    def __str__(self):
        return f"{self.user.user.username} - {self.subject.name} - Level {self.proficiency_level}"
