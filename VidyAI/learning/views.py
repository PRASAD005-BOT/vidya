from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum, Count, Avg

from core.models import UserProfile, Subject
from .models import (
    LearningStyle, UserActivity,
    Skill, Badge, UserBadge, MicroCertification, 
    UserCertification, UserSkill, UserStreak,
    SkillCategory, GamificationSettings, LearningStyleAssessment,
    UserGameProgress, LearningGame
)
from .services import (
    get_skill_heatmap_data, update_user_streak,
    record_learning_activity, check_badge_eligibility,
    check_certification_eligibility
)

# Create your views here.
@login_required
def learning_home(request):
    """Learning home page"""
    # Get user streak
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    
    # Simple context with available features
    context = {
        'title': _('Learning Center'),
        'streak': streak
    }
    return render(request, 'learning/home.html', context)

@login_required
def activities(request):
    """Learning activities"""
    context = {
        'title': _('Learning Activities')
    }
    return render(request, 'learning/activities.html', context)

@login_required
def learning_games(request):
    """Learning games"""
    # Get or update user streak
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    if not created:
        streak = update_user_streak(request.user)
    
    # Get user's skills for the heatmap
    skill_data = get_skill_heatmap_data(request.user)
    
    # Get user's badges
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge').order_by('-earned_date')[:5]
    
    # Get user's game progress
    user_progress = UserGameProgress.objects.filter(
        user=request.user.profile
    ).select_related('game').order_by('-last_played')[:5]
    
    # Record activity for visiting games
    record_learning_activity(
        user=request.user,
        activity_type='practice_session',
        description="Accessed learning games",
        points=5
    )
    
    context = {
        'title': _('Learning Games'),
        'streak': streak,
        'skill_data': skill_data,
        'user_badges': user_badges,
        'user_progress': user_progress
    }
    return render(request, 'learning/games.html', context)

@login_required
def learning_progress(request):
    """Learning progress tracking"""
    context = {
        'title': _('My Progress')
    }
    return render(request, 'learning/progress.html', context)

@login_required
def badges(request):
    """Earned badges"""
    context = {
        'title': _('My Badges')
    }
    return render(request, 'learning/badges.html', context)

@login_required
def assessment(request):
    """Learning assessment"""
    context = {
        'title': _('Assessment')
    }
    return render(request, 'learning/assessment.html', context)

@login_required
def learning_style_assessment(request):
    """Learning style assessment"""
    if request.method == 'POST':
        answers = {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.replace('question_', '')
                answers[question_id] = value
        
        # Calculate learning style based on answers
        visual_count = 0
        auditory_count = 0
        kinesthetic_count = 0
        
        for answer in answers.values():
            if answer == 'visual':
                visual_count += 1
            elif answer == 'auditory':
                auditory_count += 1
            elif answer == 'kinesthetic':
                kinesthetic_count += 1
        
        # Determine dominant style
        if visual_count >= auditory_count and visual_count >= kinesthetic_count:
            style = 'visual'
        elif auditory_count >= visual_count and auditory_count >= kinesthetic_count:
            style = 'auditory'
        else:
            style = 'kinesthetic'
        
        # Save learning style
        learning_style, created = LearningStyle.objects.get_or_create(user=request.user.profile)
        learning_style.style = style
        learning_style.visual_score = visual_count
        learning_style.auditory_score = auditory_count
        learning_style.kinesthetic_score = kinesthetic_count
        learning_style.save()
        
        # Record activity
        record_learning_activity(
            user=request.user,
            activity_type='learning_assessment',
            description="Completed learning style assessment",
            points=50
        )
        
        messages.success(request, _('Your learning style has been determined!'))
        return redirect('learning:learning_home')
    
    context = {
        'title': _('Learning Style Assessment')
    }
    return render(request, 'learning/learning_style.html', context)

@login_required
def skill_heatmap(request):
    """View for displaying the skill heatmap visualization"""
    # Get skill heatmap data
    heatmap_data = get_skill_heatmap_data(request.user)
    
    # Get global skill categories
    all_categories = SkillCategory.objects.all()
    
    context = {
        'title': _('Skill Heatmap'),
        'heatmap_data': heatmap_data,
        'all_categories': all_categories
    }
    return render(request, 'learning/skill_heatmap.html', context)

@login_required
def badges_showcase(request):
    """View for displaying badges and certifications earned"""
    # Get user's badges
    user_badges = UserBadge.objects.filter(user=request.user).select_related('badge').order_by('-earned_date')
    
    # Get user's certifications
    user_certifications = UserCertification.objects.filter(user=request.user).select_related('certification').order_by('-earned_date')
    
    # Group badges by level
    badges_by_level = {
        'platinum': user_badges.filter(badge__level='platinum'),
        'gold': user_badges.filter(badge__level='gold'),
        'silver': user_badges.filter(badge__level='silver'),
        'bronze': user_badges.filter(badge__level='bronze')
    }
    
    # Get badges progress stats
    total_badges = Badge.objects.count()
    earned_badges = user_badges.count()
    badges_progress = (earned_badges / total_badges * 100) if total_badges > 0 else 0
    
    # Get certifications progress stats
    total_certs = MicroCertification.objects.count()
    earned_certs = user_certifications.count()
    certs_progress = (earned_certs / total_certs * 100) if total_certs > 0 else 0
    
    context = {
        'title': _('Badges & Certifications'),
        'user_badges': user_badges,
        'user_certifications': user_certifications,
        'badges_by_level': badges_by_level,
        'total_badges': total_badges,
        'earned_badges': earned_badges,
        'badges_progress': badges_progress,
        'total_certs': total_certs,
        'earned_certs': earned_certs,
        'certs_progress': certs_progress
    }
    return render(request, 'learning/badges_showcase.html', context)

@login_required
def streak_stats(request):
    """View for displaying streak statistics"""
    # Get or create user streak
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    
    # Calculate daily goal progress
    daily_goal = 50  # Example: 50 points per day
    today = timezone.now().date()
    daily_progress = UserActivity.objects.filter(
        user=request.user,
        timestamp__date=today
    ).aggregate(points=Sum('points_earned'))['points'] or 0
    
    daily_goal_percent = min(100, (daily_progress / daily_goal) * 100) if daily_goal > 0 else 0
    
    # Calculate streak milestones
    milestone_3_days = streak.current_streak >= 3
    milestone_7_days = streak.current_streak >= 7
    milestone_14_days = streak.current_streak >= 14
    milestone_30_days = streak.current_streak >= 30
    
    # Get streak stats
    total_days_active = UserActivity.objects.filter(
        user=request.user
    ).values('timestamp__date').distinct().count()
    
    streak_bonus_points = (streak.current_streak * 5)  # Example: 5 bonus points per streak day
    
    avg_points_per_day = UserActivity.objects.filter(
        user=request.user
    ).values('timestamp__date').annotate(
        daily_points=Sum('points_earned')
    ).aggregate(avg=Avg('daily_points'))['avg'] or 0
    
    # Format for template
    avg_points_per_day = round(avg_points_per_day, 1)
    
    # Create calendar data (simplified for example)
    from datetime import timedelta
    
    # Generate 90 days of sample data
    calendar_data = []
    current_month = None
    month_data = None
    
    for i in range(90, 0, -1):
        date = today - timedelta(days=i)
        
        # Check if we need to start a new month
        if current_month != date.month:
            if month_data:
                calendar_data.append(month_data)
            
            current_month = date.month
            month_data = {
                'month_name': date.strftime('%b'),
                'weeks': []
            }
            current_week = []
    
        # Add activity level based on points
        points = UserActivity.objects.filter(
            user=request.user,
            timestamp__date=date
        ).aggregate(total=Sum('points_earned'))['total'] or 0
        
        activities = UserActivity.objects.filter(
            user=request.user,
            timestamp__date=date
        ).count()
        
        # Determine activity level (0-4)
        if points == 0:
            level = 0
        elif points < 20:
            level = 1
        elif points < 50:
            level = 2
        elif points < 100:
            level = 3
        else:
            level = 4
        
        day_data = {
            'date': date.strftime('%Y-%m-%d'),
            'level': level,
            'points': points,
            'activities': activities
        }
        
        current_week.append(day_data)
        
        # End of week or last day
        if date.weekday() == 6 or i == 1:
            month_data['weeks'].append(current_week)
            current_week = []
    
    # Add the last month if it exists
    if month_data:
        calendar_data.append(month_data)
    
    context = {
        'title': _('Streak Statistics'),
        'streak': streak,
        'daily_goal': daily_goal,
        'daily_progress': daily_progress,
        'daily_goal_percent': daily_goal_percent,
        'milestone_3_days': milestone_3_days,
        'milestone_7_days': milestone_7_days,
        'milestone_14_days': milestone_14_days,
        'milestone_30_days': milestone_30_days,
        'longest_streak': streak.longest_streak,
        'total_days_active': total_days_active,
        'streak_bonus_points': streak_bonus_points,
        'avg_points_per_day': avg_points_per_day,
        'calendar_data': calendar_data,
        'streak_start_date': streak.last_activity_date - timedelta(days=streak.current_streak-1) if streak.current_streak > 0 and streak.last_activity_date else today
    }
    return render(request, 'learning/streak_stats.html', context)

@login_required
def learning_stats(request):
    """View for displaying learning statistics"""
    # Get user activities
    all_activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')
    
    # Get subjects with progress
    subjects = Subject.objects.all()
    subject_progress = []
    
    for subject in subjects:
        # Calculate proficiency level (1-10) based on activities
        # Get skills affected by the user's activities that belong to categories matching this subject
        activities_count = UserActivity.objects.filter(
            user=request.user,
            skills_affected__category__name__icontains=subject.name
        ).count()
        
        # Simple formula: 1 level for every 5 activities, max 10
        proficiency_level = min(10, max(1, activities_count // 5 + 1))
        
        # Get last activity date
        last_activity = UserActivity.objects.filter(
            user=request.user,
            skills_affected__category__name__icontains=subject.name
        ).order_by('-timestamp').first()
        
        subject_progress.append({
            'subject': subject,
            'proficiency_level': proficiency_level,
            'last_activity': last_activity.timestamp if last_activity else None
        })
    
    # Time spent learning (in hours)
    # Assuming each activity takes 15 minutes on average
    total_activities = all_activities.count()
    time_spent = (total_activities * 15) / 60  # in hours
    
    # Get streak
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    
    # Get skills distribution
    skills_by_level = {}
    for i in range(1, 11):
        skills_by_level[i] = UserSkill.objects.filter(
            user=request.user,
            current_level=i
        ).count()
    
    # Calculate learning progress percentage
    total_possible_skills = Skill.objects.count() * 10  # max level for each skill
    current_progress = UserSkill.objects.filter(user=request.user).aggregate(
        total=Sum('current_level'))['total'] or 0
    
    learning_progress = (current_progress / total_possible_skills * 100) if total_possible_skills > 0 else 0
    
    # Get learning style
    try:
        learning_style = LearningStyle.objects.get(user=request.user.profile)
        style_data = {
            'name': learning_style.get_style_display(),
            'visual': learning_style.visual_score,
            'auditory': learning_style.auditory_score,
            'kinesthetic': learning_style.kinesthetic_score,
        }
    except LearningStyle.DoesNotExist:
        style_data = {
            'name': 'Not determined',
            'visual': 0,
            'auditory': 0,
            'kinesthetic': 0,
        }
    
    # Get top skills
    top_skills = UserSkill.objects.filter(
        user=request.user
    ).order_by('-current_level')[:5]
    
    # Generate timeline data
    timeline_data = []
    
    # Last 10 activities for timeline
    recent_activities = all_activities[:10]
    for activity in recent_activities:
        timeline_data.append({
            'date': activity.timestamp,
            'type': activity.activity_type,
            'description': activity.description,
            'points': activity.points_earned
        })
    
    # Add badges earned to timeline
    badges_earned = UserBadge.objects.filter(
        user=request.user
    ).order_by('-earned_date')[:5]
    
    for badge in badges_earned:
        timeline_data.append({
            'date': badge.earned_date,
            'type': 'badge_earned',
            'description': f"Earned {badge.badge.name} badge",
            'badge': badge.badge
        })
    
    # Sort timeline by date
    timeline_data.sort(key=lambda x: x['date'], reverse=True)
    timeline_data = timeline_data[:10]  # Take most recent 10 items
    
    # Get leaderboard data
    leaderboard = UserProfile.objects.order_by('-points')[:10]
    
    # Get user rank
    user_rank = 1
    for profile in UserProfile.objects.order_by('-points'):
        if profile.user == request.user:
            break
        user_rank += 1
    
    context = {
        'title': _('Learning Statistics'),
        'subject_progress': subject_progress,
        'time_spent': time_spent,
        'streak': streak,
        'skills_by_level': skills_by_level,
        'learning_progress': learning_progress,
        'style_data': style_data,
        'top_skills': top_skills,
        'timeline_data': timeline_data,
        'leaderboard': leaderboard,
        'user_rank': user_rank
    }
    return render(request, 'learning/learning_stats.html', context)