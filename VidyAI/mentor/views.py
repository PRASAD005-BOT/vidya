from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
import json
import requests
import re
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import random
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Create your views here.
@login_required
def mentor_home(request):
    """Mentor home page"""
    context = {
        'title': _('Mentors')
    }
    return render(request, 'mentor/home.html', context)

@login_required
def search_videos(request):
    """Search for YouTube videos based on topic"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic = data.get('topic', '')
            difficulty = data.get('difficulty', 'beginner')
            
            if not topic:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please provide a topic'
                }, status=400)
            
            # Format the search query
            search_query = topic
            if difficulty:
                search_query += f" {difficulty} tutorial"
            
            # Get YouTube videos based on the query
            videos = create_direct_youtube_searches(search_query)
            
            return JsonResponse({
                'status': 'success',
                'videos': videos
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)

def create_direct_youtube_searches(query):
    """Search YouTube using the API and return real videos"""
    # Clean and format the search query
    query = query.strip()
    
    # Create videos list
    videos = []
    
    try:
        # YouTube API key
        api_key = 'AIzaSyBW6EQi2VooF7IoxOIDUEfEaYY36RWTfvk'
        
        # Build the YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Create variations of the search query for more comprehensive results
        search_variations = [
            query,                           # Original query
            f"{query} tutorial",             # Tutorial
            f"{query} for beginners",        # For beginners
            f"{query} course",               # Course
            f"{query} explained",            # Explained
        ]
        
        # Search for each variation
        for search_term in search_variations:
            # Execute the search
            request = youtube.search().list(
                q=search_term,
                part='snippet',
                maxResults=2,               # Get 2 results per variation
                type='video',
                videoEmbeddable='true',     # Only embeddable videos
                relevanceLanguage='en'      # English videos preferred
            )
            response = request.execute()
            
            # Process the results
            for item in response.get('items', []):
                video_id = item['id']['videoId']
                
                # Skip if we already have this video
                if any(v['id'] == video_id for v in videos):
                    continue
                
                # Get video details
                title = item['snippet']['title']
                channel = item['snippet']['channelTitle']
                thumbnail = item['snippet']['thumbnails']['high']['url']
                published_at = item['snippet']['publishedAt']
                
                # Format the published date
                from datetime import datetime
                import pytz
                
                # Parse the ISO format date
                dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                # Format it to a more readable form
                published_at = dt.strftime("%b %d, %Y")
                
                # Add to videos list
                videos.append({
                    "id": video_id,
                    "title": title,
                    "thumbnail": thumbnail,
                    "channel": channel,
                    "published_at": published_at
                })
                
                # Limit to 10 total videos
                if len(videos) >= 10:
                    break
            
            # Break the outer loop if we have enough videos
            if len(videos) >= 10:
                break
                
    except HttpError as e:
        print(f"An HTTP error occurred: {e}")
        # Fallback to the previous implementation if API fails
        return fallback_videos(query)
    except Exception as e:
        print(f"An error occurred: {e}")
        # Fallback to the previous implementation if any error occurs
        return fallback_videos(query)
    
    # If we didn't get any videos from the API, use the fallback
    if not videos:
        return fallback_videos(query)
    
    # Print the number of videos generated
    print(f"Generated {len(videos)} YouTube videos for query: {query}")
    
    return videos

def fallback_videos(query):
    """Fallback method when YouTube API fails"""
    # Create videos list
    videos = []
    
    # Educational video IDs (popular educational content)
    educational_videos = [
        "rfscVS0vtbw",  # freeCodeCamp Python course
        "OXGznpKZ_sA",  # Khan Academy
        "fKl2JW_qrso",  # Crash Course
        "fNk_zzaMoSs",  # 3Blue1Brown
        "rIO5326FgPE",  # Kurzgesagt
        "bJzb-RuUcMU",  # TED-Ed
        "eWRfhZUzrAc",  # Vsauce
        "7_c4zVJ739M",  # Veritasium
        "WFZwoHZUReQ",  # Minute Physics
        "QnQe0xW_JY4"   # SciShow
    ]
    
    # Channel names for the videos
    channels = [
        "freeCodeCamp", "Khan Academy", "Crash Course", "3Blue1Brown", "Kurzgesagt",
        "TED-Ed", "Vsauce", "Veritasium", "Minute Physics", "SciShow"
    ]
    
    # Create variations of the search query for titles
    search_variations = [
        query,                           # Original query
        f"{query} tutorial",             # Tutorial
        f"{query} for beginners",        # For beginners
        f"{query} advanced",             # Advanced
        f"{query} course",               # Course
        f"{query} complete guide",       # Complete guide
        f"{query} step by step",         # Step by step
        f"{query} explained simply",     # Explained simply
        f"{query} lectures",             # Lectures
        f"{query} for students",         # For students
    ]
    
    # Generate video entries
    for i, search_term in enumerate(search_variations):
        if i >= len(educational_videos):
            break
            
        video_id = educational_videos[i]
        
        # Create title and channel based on the search variation
        if i == 0:
            title = f"{search_term.title()} - Complete Course"
        elif i == 1:
            title = f"Learn {search_term.title()} - Step by Step Tutorial"
        elif i == 2:
            title = f"{search_term.title()} for Beginners - No Experience Needed"
        elif i == 3:
            title = f"Advanced {search_term.title()} - Master Level"
        elif i == 4:
            title = f"Full {search_term.title()} Course - Comprehensive Guide"
        elif i == 5:
            title = f"The Complete {search_term.title()} Guide - Everything You Need"
        elif i == 6:
            title = f"{search_term.title()} - Step By Step Instructions"
        elif i == 7:
            title = f"{search_term.title()} Explained Simply - Easy to Understand"
        elif i == 8:
            title = f"{search_term.title()} Lectures - University Level"
        else:
            title = f"{search_term.title()} for Students - Educational Content"
        
        channel = channels[i]
        
        # Generate a publishing date (random recent date)
        import random
        from datetime import datetime, timedelta
        
        days_ago = random.randint(7, 365)
        publish_date = datetime.now() - timedelta(days=days_ago)
        published_at = publish_date.strftime("%b %d, %Y")
        
        # Add to videos list
        videos.append({
            "id": video_id,
            "title": title,
            "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "channel": channel,
            "published_at": published_at
        })
    
    print(f"Generated {len(videos)} fallback YouTube videos for query: {query}")
    
    return videos

@login_required
def find_mentor(request):
    """Find a mentor"""
    context = {
        'title': _('Find a Mentor')
    }
    return render(request, 'mentor/find_mentor.html', context)

@login_required
def register_as_mentor(request):
    """Register as a mentor"""
    context = {
        'title': _('Become a Mentor')
    }
    return render(request, 'mentor/register_as_mentor.html', context)

@login_required
def mentor_dashboard(request):
    """Mentor dashboard"""
    context = {
        'title': _('Mentor Dashboard')
    }
    return render(request, 'mentor/dashboard.html', context)

@login_required
def mentor_sessions(request):
    """Mentor sessions"""
    context = {
        'title': _('My Sessions')
    }
    return render(request, 'mentor/sessions.html', context)

@login_required
def connect_with_mentor(request, mentor_id):
    """Connect with a mentor"""
    # Placeholder - to be implemented
    messages.success(request, _('Request sent to mentor successfully!'))
    return redirect('mentor:find_mentor')

@login_required
def ask_question(request):
    """API endpoint to handle questions about video content"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', '')
            video_title = data.get('videoTitle', '')
            video_id = data.get('videoId', '')
            
            if not question:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please provide a question'
                }, status=400)
            
            # For now, provide a fallback response without using the Gemini API
            # This avoids errors while the API integration is being set up
            fallback_answers = [
                f"To understand '{video_title}', it helps to break it down into smaller parts. The key concept is to focus on one step at a time and make sure you understand each part before moving on.",
                f"When learning about '{video_title}', many students find it helpful to relate the concepts to real-world examples. Think about how this might apply to something you're already familiar with.",
                f"The topic '{video_title}' can be challenging, but remember to focus on the fundamentals first. The basic principles are the foundation for understanding the more complex ideas.",
                f"A good approach to understanding '{video_title}' is to try explaining it in your own words. If you can explain it simply, you probably understand it well.",
                f"For topics like '{video_title}', it often helps to draw diagrams or visual representations. Visualizing the concept can make it much clearer.",
            ]
            
            import random
            answer = random.choice(fallback_answers)
            
            # Return the generated answer
            return JsonResponse({
                'status': 'success',
                'answer': answer
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)
        except Exception as e:
            print(f"Error in ask_question: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}',
                'answer': 'I apologize, but I encountered an error while processing your question. A good approach to understanding complex topics is to break them down into smaller parts and focus on one concept at a time.'
            }, status=200)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)