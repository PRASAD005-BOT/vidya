import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vidyai.settings')
django.setup()

# Import models
from django.contrib.auth.models import User
from core.models import UserProfile, Subject, UserProgress
from tutor.models import Lesson, Quiz
from mentor.models import MentorProfile, MentorRequest, MentorSession, MentorReview
from learning.models import LearningActivity, LearningGame, UserActivityCompletion

def print_table_header(title):
    """Print a formatted table header"""
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80)

def print_users():
    """Print all User data"""
    print_table_header("USERS")
    users = User.objects.all()
    if not users:
        print("No users found.")
        return
    
    print(f"{'ID':<5} {'Username':<15} {'Email':<30} {'Full Name':<20} {'Staff':<5}")
    print("-"*80)
    for user in users:
        print(f"{user.id:<5} {user.username:<15} {user.email:<30} {user.get_full_name():<20} {user.is_staff}")

def print_user_profiles():
    """Print all UserProfile data"""
    print_table_header("USER PROFILES")
    profiles = UserProfile.objects.all()
    if not profiles:
        print("No user profiles found.")
        return
    
    print(f"{'ID':<5} {'User':<15} {'Learning Style':<20} {'Language':<10} {'Grade':<10}")
    print("-"*80)
    for profile in profiles:
        print(f"{profile.id:<5} {profile.user.username:<15} {profile.learning_style:<20} {profile.preferred_language:<10} {profile.grade:<10}")

def print_subjects():
    """Print all Subject data"""
    print_table_header("SUBJECTS")
    subjects = Subject.objects.all()
    if not subjects:
        print("No subjects found.")
        return
    
    print(f"{'ID':<5} {'Name':<20} {'Description':<50}")
    print("-"*80)
    for subject in subjects:
        # Truncate description if too long
        desc = subject.description[:47] + "..." if len(subject.description) > 47 else subject.description
        print(f"{subject.id:<5} {subject.name:<20} {desc:<50}")

def print_lessons():
    """Print all Lesson data"""
    print_table_header("LESSONS")
    lessons = Lesson.objects.all()
    if not lessons:
        print("No lessons found.")
        return
    
    print(f"{'ID':<5} {'Title':<30} {'Subject':<15} {'Difficulty':<15} {'Grade':<5}")
    print("-"*80)
    for lesson in lessons:
        print(f"{lesson.id:<5} {lesson.title[:27] + '...' if len(lesson.title) > 27 else lesson.title:<30} {lesson.subject.name[:12] + '...' if len(lesson.subject.name) > 12 else lesson.subject.name:<15} {lesson.difficulty:<15} {lesson.grade:<5}")

def print_quizzes():
    """Print all Quiz data"""
    print_table_header("QUIZZES")
    quizzes = Quiz.objects.all()
    if not quizzes:
        print("No quizzes found.")
        return
    
    print(f"{'ID':<5} {'Title':<30} {'Subject':<15} {'Grade':<5} {'Passing Score':<15}")
    print("-"*80)
    for quiz in quizzes:
        subject_name = quiz.subject.name if quiz.subject else "N/A"
        print(f"{quiz.id:<5} {quiz.title[:27] + '...' if len(quiz.title) > 27 else quiz.title:<30} {subject_name[:12] + '...' if len(subject_name) > 12 else subject_name:<15} {quiz.grade:<5} {quiz.passing_score:<15}")

def print_mentor_profiles():
    """Print all MentorProfile data"""
    print_table_header("MENTOR PROFILES")
    mentors = MentorProfile.objects.all()
    if not mentors:
        print("No mentor profiles found.")
        return
    
    print(f"{'ID':<5} {'User':<15} {'Status':<15} {'Experience':<10} {'Rating':<10}")
    print("-"*80)
    for mentor in mentors:
        print(f"{mentor.id:<5} {mentor.user.user.username:<15} {mentor.status:<15} {mentor.experience_years:<10} {mentor.rating}")

def print_learning_activities():
    """Print all LearningActivity data"""
    print_table_header("LEARNING ACTIVITIES")
    activities = LearningActivity.objects.all()
    if not activities:
        print("No learning activities found.")
        return
    
    print(f"{'ID':<5} {'Title':<30} {'Subject':<15} {'Type':<10} {'Duration':<10}")
    print("-"*80)
    for activity in activities:
        print(f"{activity.id:<5} {activity.title[:27] + '...' if len(activity.title) > 27 else activity.title:<30} {activity.subject.name[:12] + '...' if len(activity.subject.name) > 12 else activity.subject.name:<15} {activity.activity_type:<10} {activity.duration_minutes:<10}")

def print_learning_games():
    """Print all LearningGame data"""
    print_table_header("LEARNING GAMES")
    games = LearningGame.objects.all()
    if not games:
        print("No learning games found.")
        return
    
    print(f"{'ID':<5} {'Name':<30} {'Subject':<15} {'Type':<15} {'Points':<10}")
    print("-"*80)
    for game in games:
        print(f"{game.id:<5} {game.name[:27] + '...' if len(game.name) > 27 else game.name:<30} {game.subject.name[:12] + '...' if len(game.subject.name) > 12 else game.subject.name:<15} {game.game_type:<15} {game.points_reward:<10}")

def print_all_data():
    """Print all data from all tables"""
    print_users()
    print_user_profiles()
    print_subjects()
    print_lessons()
    print_quizzes()
    print_mentor_profiles()
    print_learning_activities()
    print_learning_games()
    
    # Print table counts summary
    print_table_header("DATABASE SUMMARY")
    print(f"{'Table':<30} {'Count':<10}")
    print("-"*80)
    print(f"{'Users':<30} {User.objects.count():<10}")
    print(f"{'User Profiles':<30} {UserProfile.objects.count():<10}")
    print(f"{'Subjects':<30} {Subject.objects.count():<10}")
    print(f"{'Lessons':<30} {Lesson.objects.count():<10}")
    print(f"{'Quizzes':<30} {Quiz.objects.count():<10}")
    print(f"{'Mentor Profiles':<30} {MentorProfile.objects.count():<10}")
    print(f"{'Mentor Requests':<30} {MentorRequest.objects.count():<10}")
    print(f"{'Mentor Sessions':<30} {MentorSession.objects.count():<10}")
    print(f"{'Learning Activities':<30} {LearningActivity.objects.count():<10}")
    print(f"{'Learning Games':<30} {LearningGame.objects.count():<10}")

if __name__ == "__main__":
    print_all_data() 