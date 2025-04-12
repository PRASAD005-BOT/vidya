from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Subject, UserProgress
from .utils import generate_content, extract_text_from_gemini_response
from django.utils.translation import gettext as _

# Create your views here.
def home(request):
    """Home page view"""
    context = {
        'title': _('Welcome to VidyAI++'),
    }
    return render(request, 'core/home.html', context)

def about(request):
    """About page view"""
    context = {
        'title': _('About VidyAI++'),
    }
    return render(request, 'core/about.html', context)

def register(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate form data
        if password != confirm_password:
            messages.error(request, _('Passwords do not match'))
            return redirect('core:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, _('Username already exists'))
            return redirect('core:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, _('Email already exists'))
            return redirect('core:register')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            preferred_language=request.POST.get('language', 'en'),
            school_name=request.POST.get('school_name', ''),
            grade=request.POST.get('grade', ''),
            bpl_card_number=request.POST.get('bpl_card_number', '')
        )
        
        messages.success(request, _('Account created successfully. Please log in.'))
        return redirect('core:login')
    
    context = {
        'title': _('Register'),
    }
    return render(request, 'core/register.html', context)

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('core:dashboard')
        else:
            messages.error(request, _('Invalid username or password'))
    
    context = {
        'title': _('Login'),
    }
    return render(request, 'core/login.html', context)

@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, _('Logged out successfully'))
    return redirect('core:home')

@login_required
def profile(request):
    """User profile view"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update profile
        profile.preferred_language = request.POST.get('language', profile.preferred_language)
        profile.school_name = request.POST.get('school_name', profile.school_name)
        profile.grade = request.POST.get('grade', profile.grade)
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        messages.success(request, _('Profile updated successfully'))
        return redirect('core:profile')
    
    context = {
        'title': _('My Profile'),
        'profile': profile,
    }
    return render(request, 'core/profile.html', context)

@login_required
def dashboard(request):
    """User dashboard view"""
    profile = request.user.profile
    
    # Get user progress on subjects
    subject_progress = UserProgress.objects.filter(user=profile)
    
    # Generate a personalized welcome message
    welcome_prompt = f"Generate a short, personalized, motivational message for a student named {request.user.first_name or request.user.username} who is in grade {profile.grade}. Keep it under 100 words and make it inspiring for learning."
    
    try:
        welcome_response = generate_content(welcome_prompt, profile.preferred_language)
        welcome_message = extract_text_from_gemini_response(welcome_response)
    except Exception as e:
        welcome_message = _("Welcome back to VidyAI++! Ready to continue your learning journey?")
    
    context = {
        'title': _('Dashboard'),
        'profile': profile,
        'subject_progress': subject_progress,
        'welcome_message': welcome_message,
    }
    return render(request, 'core/dashboard.html', context)
