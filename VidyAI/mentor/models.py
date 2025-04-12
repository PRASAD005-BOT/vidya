from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import UserProfile, Subject

# Create your models here.
class MentorProfile(models.Model):
    MENTOR_STATUS_CHOICES = [
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('declined', _('Declined')),
        ('inactive', _('Inactive')),
    ]
    
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='mentor_profile')
    bio = models.TextField()
    expertise = models.ManyToManyField(Subject, related_name='mentors')
    qualification = models.CharField(max_length=255)
    experience_years = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=MENTOR_STATUS_CHOICES, default='pending')
    availability = models.TextField(blank=True, help_text=_('Describe your availability schedule'))
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_sessions = models.PositiveIntegerField(default=0)
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.user.username} - Mentor"

class MentorRequest(models.Model):
    REQUEST_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('declined', _('Declined')),
        ('cancelled', _('Cancelled')),
        ('completed', _('Completed')),
    ]
    
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='mentor_requests')
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='requests')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Request from {self.student.user.username} to {self.mentor.user.user.username}"

class MentorSession(models.Model):
    SESSION_STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('ongoing', _('Ongoing')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('missed', _('Missed')),
    ]
    
    request = models.ForeignKey(MentorRequest, on_delete=models.CASCADE, related_name='sessions')
    session_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='scheduled')
    meeting_link = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Session with {self.request.mentor.user.user.username} - {self.session_date}"

class MentorReview(models.Model):
    session = models.OneToOneField(MentorSession, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.session.request.mentor.user.user.username} - {self.rating}/5"

class AImentorSuggestion(models.Model):
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='mentor_suggestions')
    suggested_mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='ai_suggestions')
    compatibility_score = models.DecimalField(max_digits=5, decimal_places=2)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_matched = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Suggestion for {self.student.user.username}: {self.suggested_mentor.user.user.username} ({self.compatibility_score})"
