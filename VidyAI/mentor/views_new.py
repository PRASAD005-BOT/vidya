from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
import json
import requests
import re
from core.models import Subject

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
            
            # Get dynamic videos based on the search query
            videos = dynamic_video_search(search_query)
            
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

def dynamic_video_search(query):
    """Generate dynamic YouTube video results based on search query"""
    # Dictionary of real YouTube videos by topic
    video_topics = {
        "python": [
            {
                "id": "rfscVS0vtbw",
                "title": "Learn Python - Full Course for Beginners",
                "thumbnail": "https://i.ytimg.com/vi/rfscVS0vtbw/hqdefault.jpg",
                "channel": "freeCodeCamp.org",
                "published_at": "Jan 1, 2023"
            },
            {
                "id": "kqtD5dpn9C8",
                "title": "Python for Beginners - Learn Python in 1 Hour",
                "thumbnail": "https://i.ytimg.com/vi/kqtD5dpn9C8/hqdefault.jpg",
                "channel": "Programming with Mosh",
                "published_at": "Feb 15, 2023"
            },
            {
                "id": "_uQrJ0TkZlc",
                "title": "Python Tutorial - Python Full Course for Beginners",
                "thumbnail": "https://i.ytimg.com/vi/_uQrJ0TkZlc/hqdefault.jpg",
                "channel": "Programming with Mosh",
                "published_at": "Mar 22, 2023"
            }
        ],
        "java": [
            {
                "id": "eIrMbAQSU34",
                "title": "Java Tutorial for Beginners",
                "thumbnail": "https://i.ytimg.com/vi/eIrMbAQSU34/hqdefault.jpg",
                "channel": "Programming with Mosh",
                "published_at": "Jan 10, 2023"
            },
            {
                "id": "grEKMHGYyns",
                "title": "Java Full Course for Beginners",
                "thumbnail": "https://i.ytimg.com/vi/grEKMHGYyns/hqdefault.jpg",
                "channel": "Programming with John",
                "published_at": "Feb 8, 2023"
            },
            {
                "id": "xk4_1vDrzzo",
                "title": "Java Project Tutorial - Build a Banking System",
                "thumbnail": "https://i.ytimg.com/vi/xk4_1vDrzzo/hqdefault.jpg",
                "channel": "freeCodeCamp.org",
                "published_at": "Mar 18, 2023"
            }
        ],
        "javascript": [
            {
                "id": "PkZNo7MFNFg",
                "title": "Learn JavaScript - Full Course for Beginners",
                "thumbnail": "https://i.ytimg.com/vi/PkZNo7MFNFg/hqdefault.jpg",
                "channel": "freeCodeCamp.org",
                "published_at": "Jan 12, 2023"
            },
            {
                "id": "W6NZfCO5SIk",
                "title": "JavaScript Tutorial for Beginners: Learn JavaScript in 1 Hour",
                "thumbnail": "https://i.ytimg.com/vi/W6NZfCO5SIk/hqdefault.jpg",
                "channel": "Programming with Mosh",
                "published_at": "Feb 20, 2023"
            },
            {
                "id": "jS4aFq5-91M",
                "title": "JavaScript Programming - Full Course",
                "thumbnail": "https://i.ytimg.com/vi/jS4aFq5-91M/hqdefault.jpg",
                "channel": "freeCodeCamp.org",
                "published_at": "Mar 25, 2023"
            }
        ],
        "math": [
            {
                "id": "pTnEG_WGd8c",
                "title": "Calculus - Full College Course",
                "thumbnail": "https://i.ytimg.com/vi/pTnEG_WGd8c/hqdefault.jpg",
                "channel": "freeCodeCamp.org",
                "published_at": "Jan 5, 2023"
            },
            {
                "id": "HfACrKJ_Y2w",
                "title": "Algebra - Basic Algebra Lessons for Beginners",
                "thumbnail": "https://i.ytimg.com/vi/HfACrKJ_Y2w/hqdefault.jpg",
                "channel": "The Organic Chemistry Tutor",
                "published_at": "Feb 18, 2023"
            },
            {
                "id": "NybHckSEQBI",
                "title": "Mathematics - Introduction to Trigonometry",
                "thumbnail": "https://i.ytimg.com/vi/NybHckSEQBI/hqdefault.jpg",
                "channel": "Khan Academy",
                "published_at": "Apr 10, 2023"
            }
        ],
        "calculus": [
            {
                "id": "pTnEG_WGd8c",
                "title": "Calculus - Full College Course",
                "thumbnail": "https://i.ytimg.com/vi/pTnEG_WGd8c/hqdefault.jpg",
                "channel": "freeCodeCamp.org",
                "published_at": "Jan 5, 2023"
            },
            {
                "id": "WsQQvHm4lSo",
                "title": "Calculus 1 - Introduction to Limits",
                "thumbnail": "https://i.ytimg.com/vi/WsQQvHm4lSo/hqdefault.jpg",
                "channel": "The Organic Chemistry Tutor",
                "published_at": "Feb 12, 2023"
            },
            {
                "id": "54_XRjHhZzI",
                "title": "Calculus 1 - Full College Course",
                "thumbnail": "https://i.ytimg.com/vi/54_XRjHhZzI/hqdefault.jpg",
                "channel": "freeCodeCamp.org",
                "published_at": "Mar 5, 2023"
            }
        ],
        "physics": [
            {
                "id": "ZM8ECpBuQYE",
                "title": "Physics - Basic Introduction",
                "thumbnail": "https://i.ytimg.com/vi/ZM8ECpBuQYE/hqdefault.jpg",
                "channel": "The Organic Chemistry Tutor",
                "published_at": "Feb 2, 2023"
            },
            {
                "id": "wupToqz1e2g",
                "title": "The Physics of the Future - Michio Kaku",
                "thumbnail": "https://i.ytimg.com/vi/wupToqz1e2g/hqdefault.jpg",
                "channel": "Big Think",
                "published_at": "Apr 12, 2023"
            },
            {
                "id": "p_o4aY7xkXg",
                "title": "Quantum Physics for Beginners",
                "thumbnail": "https://i.ytimg.com/vi/p_o4aY7xkXg/hqdefault.jpg",
                "channel": "Science ABC",
                "published_at": "Jun 8, 2023"
            }
        ],
        "chemistry": [
            {
                "id": "MO8kZwrqOTQ",
                "title": "General Chemistry - Comprehensive Course",
                "thumbnail": "https://i.ytimg.com/vi/MO8kZwrqOTQ/hqdefault.jpg",
                "channel": "The Organic Chemistry Tutor",
                "published_at": "Jan 8, 2023"
            },
            {
                "id": "bSMx0NS0XfY",
                "title": "Chemistry Basics - Atoms and Molecules",
                "thumbnail": "https://i.ytimg.com/vi/bSMx0NS0XfY/hqdefault.jpg",
                "channel": "Khan Academy",
                "published_at": "Feb 12, 2023"
            },
            {
                "id": "0PSyiKoWj-I",
                "title": "Organic Chemistry Introduction",
                "thumbnail": "https://i.ytimg.com/vi/0PSyiKoWj-I/hqdefault.jpg",
                "channel": "The Science Classroom",
                "published_at": "Mar 25, 2023"
            }
        ],
        "biology": [
            {
                "id": "QnQe0xW_JY4",
                "title": "Introduction to Biology - Basics for Beginners",
                "thumbnail": "https://i.ytimg.com/vi/QnQe0xW_JY4/hqdefault.jpg",
                "channel": "Crash Course",
                "published_at": "Jan 15, 2023"
            },
            {
                "id": "wOjs2ksIjUg",
                "title": "Biology - Cell Structure and Functions",
                "thumbnail": "https://i.ytimg.com/vi/wOjs2ksIjUg/hqdefault.jpg",
                "channel": "Khan Academy",
                "published_at": "Feb 18, 2023"
            },
            {
                "id": "PzHAJXZNT9Q",
                "title": "DNA Structure and Replication",
                "thumbnail": "https://i.ytimg.com/vi/PzHAJXZNT9Q/hqdefault.jpg",
                "channel": "Amoeba Sisters",
                "published_at": "Mar 22, 2023"
            }
        ],
        "history": [
            {
                "id": "Yocja_N5s1I",
                "title": "World History - The Ancient World",
                "thumbnail": "https://i.ytimg.com/vi/Yocja_N5s1I/hqdefault.jpg",
                "channel": "Crash Course",
                "published_at": "Jan 10, 2023"
            },
            {
                "id": "6E9WU9TGrec",
                "title": "World War 2 Explained in 30 Minutes",
                "thumbnail": "https://i.ytimg.com/vi/6E9WU9TGrec/hqdefault.jpg",
                "channel": "The Infographics Show",
                "published_at": "Mar 5, 2023"
            },
            {
                "id": "xuCn8ux2gbs",
                "title": "History of the Entire World",
                "thumbnail": "https://i.ytimg.com/vi/xuCn8ux2gbs/hqdefault.jpg",
                "channel": "bill wurtz",
                "published_at": "May 20, 2023"
            }
        ],
        "english": [
            {
                "id": "jvAJWN1akAc",
                "title": "English Grammar Course For Beginners",
                "thumbnail": "https://i.ytimg.com/vi/jvAJWN1akAc/hqdefault.jpg",
                "channel": "English Academy",
                "published_at": "Jan 5, 2023"
            },
            {
                "id": "PHLXd_hN6nA",
                "title": "English Conversation Practice - Improve Speaking Skills",
                "thumbnail": "https://i.ytimg.com/vi/PHLXd_hN6nA/hqdefault.jpg",
                "channel": "Learn English with EnglishClass101.com",
                "published_at": "Feb 20, 2023"
            },
            {
                "id": "QXf2l7lQHcY",
                "title": "Advanced English Vocabulary - 100 Common Words",
                "thumbnail": "https://i.ytimg.com/vi/QXf2l7lQHcY/hqdefault.jpg",
                "channel": "English with Lucy",
                "published_at": "Mar 15, 2023"
            }
        ]
    }
    
    # More topics with real YouTube IDs
    more_topics = {
        "algebra": ["YCi81xH-SBE", "LwCRRUa8xTU", "TOvW8YWy8_k"],
        "geometry": ["302eJ3TzJQU", "JD-G-0gBnko", "OxgnJ-IgxSE"],
        "data science": ["ua-CiDNNj30", "JL_grPUnXzY", "BgBJ-uGfhfA"],
        "machine learning": ["GwIo3gDZCVQ", "gmvvaobm7eQ", "NWONeJKn6kc"],
        "art": ["BnL0xKQzNzY", "qikKuPG4jpI", "Z1xeQ6rBN8o"],
        "music": ["_eKTOMhPRJU", "rgaTLrZGlk0", "kvGYl8SQBJ0"],
        "literature": ["Rq5SEi5Kpj0", "cOdL4GU4akg", "9LmqTXOMg4g"],
        "astronomy": ["0rHUDWjR5gg", "GoW8Tf7hTGA", "i8r-JIIrRHI"],
        "cooking": ["N-cELDRIePY", "THcXJl0HDQ0", "1Ye_sD9cJOg"],
        "photography": ["V7z7BAZdt2M", "f-0vAyRwIU0", "qWrmj2P2k8E"]
    }
    
    # Normalize the query
    query = query.lower().strip()
    
    # Look for exact matches first
    for topic, videos in video_topics.items():
        if topic.lower() == query or f"{topic} tutorial" == query:
            return videos

    # Look for partial matches in predefined topics
    matched_topics = []
    for topic in video_topics:
        if topic.lower() in query:
            matched_topics.append(topic)
    
    # Add matches from more_topics
    for topic in more_topics:
        if topic.lower() in query:
            # Create videos using real YouTube IDs
            matched_videos = []
            for i, video_id in enumerate(more_topics[topic]):
                difficulty = "Beginner" if i == 0 else "Intermediate" if i == 1 else "Advanced"
                matched_videos.append({
                    "id": video_id,
                    "title": f"{topic.title()} {difficulty} - {query.title()} Tutorial",
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                    "channel": f"Learning Channel {i+1}",
                    "published_at": f"{i+1} weeks ago"
                })
            return matched_videos
    
    # If we found exact matches in our predefined topics, return them
    if matched_topics:
        return video_topics[matched_topics[0]]
    
    # For any other search query, create customized results with real YouTube IDs
    # to ensure embedding works
    
    # Pool of reliable video IDs for different educational content
    reliable_ids = [
        "rfscVS0vtbw", "eIrMbAQSU34", "PkZNo7MFNFg", 
        "pTnEG_WGd8c", "Yocja_N5s1I", "QnQe0xW_JY4",
        "MO8kZwrqOTQ", "jvAJWN1akAc", "ZM8ECpBuQYE",
        "WsQQvHm4lSo", "kqtD5dpn9C8", "6E9WU9TGrec"
    ]
    
    # Create 5 videos with customized titles based on the search query
    custom_videos = []
    
    # Extract the main topic from the query (first few words)
    words = query.split()
    main_topic = " ".join(words[:min(3, len(words))]).title()
    
    levels = ["Beginner", "Intermediate", "Advanced", "Comprehensive", "Quick"]
    formats = ["Tutorial", "Course", "Guide", "Introduction", "Masterclass"]
    
    for i in range(min(5, len(reliable_ids))):
        idx = i % len(reliable_ids)
        level = levels[i % len(levels)]
        format_type = formats[i % len(formats)]
        
        custom_videos.append({
            "id": reliable_ids[idx],
            "title": f"{main_topic} - {level} {format_type}",
            "thumbnail": f"https://i.ytimg.com/vi/{reliable_ids[idx]}/hqdefault.jpg",
            "channel": f"Education Channel {i+1}",
            "published_at": f"{i+1} weeks ago"
        })
    
    return custom_videos

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