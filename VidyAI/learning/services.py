from django.utils import timezone
from django.db.models import Sum
from .models import UserSkill, Badge, UserBadge, MicroCertification, UserCertification, UserStreak, UserActivity

def check_badge_eligibility(user, skill=None):
    """
    Check if user is eligible for new badges
    
    Args:
        user: User to check
        skill: Optional specific skill to check badges for
    """
    # Get badges not yet earned by user
    earned_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
    available_badges = Badge.objects.exclude(id__in=earned_badge_ids)
    
    # Filter by skill if provided
    if skill:
        available_badges = available_badges.filter(skill=skill)
    
    # Check each badge
    for badge in available_badges:
        requirements = badge.get_requirements_dict()
        
        # Check skill level requirement
        if 'skill_level' in requirements and badge.skill:
            try:
                user_skill = UserSkill.objects.get(user=user, skill=badge.skill)
                if user_skill.current_level < requirements['skill_level']:
                    continue  # Requirement not met
            except UserSkill.DoesNotExist:
                continue  # User doesn't have this skill
        
        # Check multiple skills requirement
        if 'skills' in requirements:
            requirement_met = True
            for skill_data in requirements['skills']:
                try:
                    user_skill = UserSkill.objects.get(user=user, skill_id=skill_data['id'])
                    if user_skill.current_level < skill_data['level']:
                        requirement_met = False
                        break
                except UserSkill.DoesNotExist:
                    requirement_met = False
                    break
            
            if not requirement_met:
                continue
        
        # Check activity count
        if 'activity_count' in requirements:
            activity_count = UserActivity.objects.filter(
                user=user, 
                activity_type=requirements.get('activity_type', '')
            ).count()
            
            if activity_count < requirements['activity_count']:
                continue
        
        # Check points threshold
        if 'points_threshold' in requirements:
            total_points = UserActivity.objects.filter(user=user).aggregate(
                total=Sum('points_earned'))['total'] or 0
            
            if total_points < requirements['points_threshold']:
                continue
        
        # Check streak requirement
        if 'streak_days' in requirements:
            try:
                user_streak = UserStreak.objects.get(user=user)
                if user_streak.current_streak < requirements['streak_days']:
                    continue
            except UserStreak.DoesNotExist:
                continue
        
        # All requirements met, award the badge
        UserBadge.objects.create(user=user, badge=badge)
        
        # Record activity
        UserActivity.objects.create(
            user=user,
            activity_type='badge_earned',
            description=f"Earned the {badge.get_level_display()} badge: {badge.name}",
            points_earned=badge.points
        )

def check_certification_eligibility(user):
    """
    Check if user is eligible for certifications
    
    Args:
        user: User to check
    """
    # Get certifications not yet earned
    earned_cert_ids = UserCertification.objects.filter(user=user).values_list('certification_id', flat=True)
    available_certs = MicroCertification.objects.exclude(id__in=earned_cert_ids)
    
    for cert in available_certs:
        # Check if user has required skills at sufficient levels
        skill_requirements_met = True
        for skill in cert.skills.all():
            try:
                user_skill = UserSkill.objects.get(user=user, skill=skill)
                # Assume skill must be at least level 5 for certification
                if user_skill.current_level < 5:
                    skill_requirements_met = False
                    break
            except UserSkill.DoesNotExist:
                skill_requirements_met = False
                break
        
        if not skill_requirements_met:
            continue
            
        # Check if user has all required badges
        badge_requirements_met = True
        required_badge_ids = cert.required_badges.all().values_list('id', flat=True)
        earned_badges = UserBadge.objects.filter(user=user, badge_id__in=required_badge_ids).count()
        
        if earned_badges < cert.required_badges.count():
            badge_requirements_met = False
        
        if not badge_requirements_met:
            continue
        
        # All requirements met, award the certification
        UserCertification.objects.create(user=user, certification=cert)
        
        # Record activity
        UserActivity.objects.create(
            user=user,
            activity_type='certification_earned',
            description=f"Earned the {cert.name} certification",
            points_earned=cert.points
        )

def update_user_streak(user):
    """
    Update the user's streak
    
    Args:
        user: User to update streak for
    """
    streak, created = UserStreak.objects.get_or_create(user=user)
    streak.update_streak()
    
    # Check for streak milestones and award bonus points
    if not created and streak.current_streak > 0:
        milestone_points = 0
        description = ""
        
        # Daily login streak continued
        milestone_points += 10
        description = f"Daily login streak: {streak.current_streak} days"
        
        # Weekly milestone (7 days)
        if streak.current_streak % 7 == 0:
            milestone_points += 50
            description = f"Weekly streak milestone: {streak.current_streak // 7} weeks"
        
        # Monthly milestone (30 days)
        if streak.current_streak % 30 == 0:
            milestone_points += 200
            description = f"Monthly streak milestone: {streak.current_streak // 30} months"
        
        # Record activity if points earned
        if milestone_points > 0:
            UserActivity.objects.create(
                user=user,
                activity_type='streak_milestone',
                description=description,
                points_earned=milestone_points
            )
    
    return streak

def record_learning_activity(user, activity_type, description, points, skills=None):
    """
    Record a learning activity and update related gamification metrics
    
    Args:
        user: User performing the activity
        activity_type: Type of activity (from ACTIVITY_TYPES)
        description: Description of the activity
        points: Points earned for the activity
        skills: Optional list of skills affected by this activity
    """
    # Create activity record
    activity = UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        description=description,
        points_earned=points
    )
    
    # Add skills if provided
    if skills:
        activity.skills_affected.set(skills)
    
    # Update streaks
    update_user_streak(user)
    
    # Update skills
    if skills:
        for skill in skills:
            user_skill, created = UserSkill.objects.get_or_create(
                user=user, 
                skill=skill,
                defaults={'current_level': 1, 'progress_to_next': 0.0}
            )
            
            # Different activities boost skills by different amounts
            progress_amount = 0.0
            if activity_type == 'quiz_completion':
                progress_amount = 0.2
            elif activity_type == 'course_progress':
                progress_amount = 0.1
            elif activity_type == 'challenge_win':
                progress_amount = 0.3
            else:
                progress_amount = 0.05
                
            user_skill.increase_progress(progress_amount)
    
    # Check for new badges
    check_badge_eligibility(user)
    
    # Check for certifications
    check_certification_eligibility(user)
    
    return activity

def get_skill_heatmap_data(user):
    """
    Get data for a skill heatmap visualization
    
    Args:
        user: User to get heatmap for
        
    Returns:
        Dictionary with skill heatmap data
    """
    user_skills = UserSkill.objects.filter(user=user).select_related('skill', 'skill__category')
    
    categories = {}
    for user_skill in user_skills:
        category_name = user_skill.skill.category.name
        
        if category_name not in categories:
            categories[category_name] = {
                'name': category_name,
                'color': user_skill.skill.category.color,
                'icon': user_skill.skill.category.icon,
                'skills': []
            }
        
        # Add skill data
        categories[category_name]['skills'].append({
            'id': user_skill.skill.id,
            'name': user_skill.skill.name,
            'level': user_skill.current_level,
            'max_level': user_skill.skill.max_level,
            'progress': user_skill.progress_to_next,
            'icon': user_skill.skill.icon,
            'last_activity': user_skill.last_activity.strftime('%Y-%m-%d %H:%M')
        })
    
    return list(categories.values())