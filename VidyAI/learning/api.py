from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import logging

from .models import (
    UserSkill, Skill, Badge, UserBadge, MicroCertification, 
    UserCertification, UserStreak, LearningGame, UserGameProgress
)
from .services import (
    record_learning_activity, check_badge_eligibility,
    check_certification_eligibility, update_user_streak
)

logger = logging.getLogger(__name__)

@login_required
@require_POST
@ensure_csrf_cookie
def track_game_progress(request):
    """API endpoint to track game progress"""
    try:
        # Get data from request
        game_type = request.POST.get('game_type')
        score = int(request.POST.get('score', 0))
        level = int(request.POST.get('level', 1))
        completion_percentage = float(request.POST.get('completion_percentage', 100))
        
        # Find or create game object
        game, created = LearningGame.objects.get_or_create(
            game_type=game_type,
            defaults={
                'name': f"{game_type.title()} Game",
                'description': f"Auto-created {game_type} game",
                'points_reward': 10
            }
        )
        
        # Get or create user progress
        progress, created = UserGameProgress.objects.get_or_create(
            user=request.user.profile,
            game=game,
            defaults={
                'score': score,
                'highest_level': level,
                'completion_percentage': completion_percentage
            }
        )
        
        # Update if better score or level
        if not created:
            progress.score = max(progress.score, score)
            progress.highest_level = max(progress.highest_level, level)
            progress.completion_percentage = max(progress.completion_percentage, completion_percentage)
            progress.save()
        
        # Record learning activity
        activity = record_learning_activity(
            user=request.user,
            activity_type='game_completion',
            description=f"Completed {game_type} game with score {score}",
            points=score // 10,  # 1 point for each 10 score points
            skills=None  # Will be handled separately
        )
        
        # Get newly earned badges (if any)
        previous_badges = set(UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True))
        check_badge_eligibility(request.user)
        current_badges = set(UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True))
        new_badge_ids = current_badges - previous_badges
        
        # Get badge details
        new_badges = []
        if new_badge_ids:
            badges = Badge.objects.filter(id__in=new_badge_ids)
            for badge in badges:
                new_badges.append({
                    'name': badge.name,
                    'description': badge.description,
                    'level': badge.get_level_display(),
                    'icon': badge.icon,
                    'points': badge.points
                })
        
        # Get newly earned certifications (if any)
        previous_certs = set(UserCertification.objects.filter(user=request.user).values_list('certification_id', flat=True))
        check_certification_eligibility(request.user)
        current_certs = set(UserCertification.objects.filter(user=request.user).values_list('certification_id', flat=True))
        new_cert_ids = current_certs - previous_certs
        
        # Get certification details
        new_certifications = []
        if new_cert_ids:
            certifications = MicroCertification.objects.filter(id__in=new_cert_ids)
            for cert in certifications:
                new_certifications.append({
                    'name': cert.name,
                    'description': cert.description,
                    'icon': cert.icon,
                    'points': cert.points
                })
        
        # Update streak
        streak = update_user_streak(request.user)
        
        # Return success with any new achievements
        return JsonResponse({
            'success': True,
            'score': score,
            'level': level,
            'badges_earned': new_badges,
            'certifications_earned': new_certifications,
            'streak': streak.current_streak,
            'skills_updated': []  # Will be populated by update_skills endpoint
        })
        
    except Exception as e:
        logger.error(f"Error tracking game progress: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_POST
@ensure_csrf_cookie
def update_skills(request):
    """API endpoint to update skills based on game performance"""
    try:
        # Get data from request
        skills_json = request.POST.get('skills', '[]')
        score = int(request.POST.get('score', 0))
        
        skills_list = json.loads(skills_json)
        updated_skills = []
        
        for skill_name in skills_list:
            # Find or create the skill
            skill, created = Skill.objects.get_or_create(
                name=skill_name.replace('_', ' ').title(),
                defaults={
                    'description': f"Auto-created skill for {skill_name}",
                }
            )
            
            # Update user's skill
            user_skill, created = UserSkill.objects.get_or_create(
                user=request.user,
                skill=skill,
                defaults={'current_level': 1, 'progress_to_next': 0.0}
            )
            
            # Calculate progress amount based on score
            progress_amount = min(0.5, max(0.05, score / 1000))
            
            # Store original level for comparison
            original_level = user_skill.current_level
            original_progress = user_skill.progress_to_next
            
            # Update skill progress
            user_skill.increase_progress(progress_amount)
            
            # Add to updated skills if progress changed significantly or level increased
            if user_skill.current_level > original_level or user_skill.progress_to_next > original_progress + 0.05:
                updated_skills.append({
                    'name': skill.name,
                    'level': user_skill.current_level,
                    'progress': user_skill.progress_to_next,
                    'improved': user_skill.current_level > original_level
                })
        
        # Return success with updated skills
        return JsonResponse({
            'success': True,
            'skills_updated': updated_skills
        })
        
    except Exception as e:
        logger.error(f"Error updating skills: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 