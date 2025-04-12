# VidyAI++ - Multilingual AI Tutoring & Mentorship Platform

## Selected Domain
Education Technology (EdTech) focusing on accessibility and personalized learning

## Problem Statement / Use Case
To develop an inclusive, AI-powered educational platform that bridges the digital and educational divide for underprivileged students across India, providing personalized learning experiences in regional languages with real-time adaptation based on emotional and cognitive states.

## Abstract / Problem Description
VidyAI++ addresses the critical gap in quality education access for underprivileged students in India by leveraging AI for personalized learning. Students from economically disadvantaged backgrounds often face barriers to quality education due to language constraints, inadequate learning resources, and limited access to expert mentors.

Our solution is a comprehensive AI-powered educational platform that provides:
1. Real-time emotion detection during video-based learning to identify confusion and offer immediate assistance
2. Multilingual content delivery in 10+ Indian languages aligned with regional curricula
3. Adaptive learning pathways that adjust based on detected learning styles and proficiency levels
4. AI-facilitated mentor-student matching to provide human guidance where needed
5. Accessible interface designed for low-resource environments with offline capabilities

The platform uniquely combines computer vision for emotion analysis with generative AI for personalized content creation. When the system detects confusion through facial expressions, it automatically pauses the educational video and offers contextual explanations or connects students with mentors. This real-time adaptive approach ensures students receive timely support rather than falling behind, reducing dropout rates and improving learning outcomes for some of India's most vulnerable students.

## Tech Stack Used
- **Backend**: Django 4.2.10
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI/ML**: 
  - Google Gemini API for content generation and question answering
  - Face-API.js for facial expression analysis and emotion detection
  - YouTube API for video integration
- **Database**: 
  - SQLite (Development)
  - PostgreSQL (Production)
- **Deployment**: Render platform
- **Other Technologies**:
  - WebRTC for webcam access
  - WhiteNoise for static file serving
  - Gunicorn for WSGI HTTP server

## Project Explanation
VidyAI++ is an intelligent, accessible learning platform designed to provide personalized education for underprivileged students across India. Here's how the system works:

### Core Features:

1. **Emotion-Aware Learning**
   - Webcam-based emotion detection monitors student's facial expressions during video lessons
   - When confusion or frustration is detected, the system pauses the video automatically
   - A help dialog appears allowing the student to ask questions about the confusing content
   - AI-generated explanations provide immediate assistance tailored to the student's needs

2. **Multilingual Content Delivery**
   - Supports 10+ Indian languages including Hindi, Tamil, Telugu, Bengali, etc.
   - Educational content is presented in the student's preferred language
   - Translation is handled seamlessly for both content and UI elements

3. **Adaptive Learning Pathways**
   - Initial assessment categorizes students as visual, auditory, or kinesthetic learners
   - Content delivery adapts to match the student's learning style
   - Difficulty adjusts in real-time based on detected comprehension levels
   - Personalized study plans are generated based on performance data

4. **Mentor-Student Matching**
   - AI analyzes student profiles, learning patterns, and academic needs
   - Matches students with suitable mentors based on expertise and compatibility
   - Facilitates scheduling and conducting virtual mentoring sessions
   - Provides tools for feedback and progress tracking

5. **Inclusive Access Design**
   - Low-bandwidth optimized for rural and limited connectivity areas
   - Offline mode for accessing previously downloaded content
   - Voice navigation for students with limited literacy
   - Simplified UI with clear visual cues and minimal text dependency

### Technical Implementation:

1. **Emotion Detection System**
   - Uses Face-API.js to detect facial expressions through webcam
   - Analyzes expressions to identify confusion, frustration, engagement, etc.
   - Processes emotion data in real-time (every 1000ms)
   - Triggers interventions when negative emotions persist

2. **Video Learning Integration**
   - YouTube API integration for educational content delivery
   - Custom video player with pause/play controls
   - Event handling for video state changes
   - Integration with emotion detection for adaptive playback

3. **AI Content Generation**
   - Google Gemini API for generating explanations and answering questions
   - Contextual awareness of current video topic
   - Ability to simplify complex concepts based on detected confusion
   - Language adaptation for regional preferences

4. **User Progress Tracking**
   - Comprehensive analytics on learning patterns and emotional responses
   - Identification of challenging topics based on confusion frequency
   - Progress visualization through skill heatmaps and achievement badges
   - Streak-based motivation system to encourage regular engagement

### Impact and Innovation:

VidyAI++ addresses critical educational challenges in India by:
- Making quality education accessible regardless of geographic or economic barriers
- Providing real-time support that mimics personalized tutoring at scale
- Accommodating diverse learning needs across India's linguistic landscape
- Creating an inclusive platform that adapts to students rather than requiring them to adapt
- Leveraging cutting-edge AI to democratize access to personalized education

The platform's innovative emotion detection features ensure students aren't left behind when they encounter difficult concepts, immediately providing the support they need to succeed.

## Deploying to Render

### Option 1: Using render.yaml (Recommended)

1. Fork or clone this repository to your GitHub account
2. Log in to your Render dashboard (https://dashboard.render.com/)
3. Click "New" and select "Blueprint" from the dropdown
4. Connect your GitHub repository
5. Render will automatically configure your web service and database from the `render.yaml` file
6. Add the following environment variable in your Render dashboard:
   - `GEMINI_API_KEY`: Your Google Gemini API key for AI features

### Option 2: Manual Deployment

1. In your Render dashboard, create a new Web Service
2. Connect your GitHub repository
3. Configure the following settings:
   - **Name**: `vidyai` (or your preferred name)
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt && cd VidyAI && python manage.py collectstatic --no-input && python manage.py migrate`
   - **Start Command**: `cd VidyAI && gunicorn vidyai.wsgi:application`
4. Add the required environment variables:
   - `SECRET_KEY`: Generate a secure random string
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `DJANGO_SETTINGS_MODULE`: vidyai.settings
5. Create a PostgreSQL database in Render and link it to your web service

### Project Structure Note

This project has the Django application in the `VidyAI` subdirectory. The deployment configuration handles this by changing to that directory before running Django commands.

## Roadmap

- Integration with regional school curricula and syllabi
- Mobile app development with offline functionality
- Enhanced voice-based interaction features
- Advanced vision-based learning analytics
- Support for additional languages and dialects

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Google Gemini API for AI capabilities
- National Education Policy (NEP) for educational framework guidance
- Django for the robust web framework
- Bootstrap for the responsive design components
- ##images
- ![home page](https://github.com/user-attachments/assets/cd9ee61d-0c78-4bed-ae55-3a876218dac2)
- ![night visoin dark mode](https://github.com/user-attachments/assets/a2d1738d-c79b-436e-827c-d57ed4f18889)
- ![profile update](https://github.com/user-attachments/assets/98d6b099-aefc-482a-90a8-e6726fad69b1)
- ![dashboard](https://github.com/user-attachments/assets/04e7df37-51cd-444a-ab5a-e85ecc01e5ca)
- ![dashboard2](https://github.com/user-attachments/assets/d5f03507-9aee-4cfa-b25b-c748a75a5ffe)
- ![voice sppech mutlilanguage](https://github.com/user-attachments/assets/2d50bba0-b069-436f-a19d-2c8146a50c80)
- ![multilang](https://github.com/user-attachments/assets/c15c3278-1a3a-4745-bba0-a8dfaf3ba210)
- ![multi lang](https://github.com/user-attachments/assets/b9096ca9-1a0b-4607-9cbf-eefbdeddee0e)
- ![Quiz](https://github.com/user-attachments/assets/4f78d0e1-fb6f-47e9-87f7-089a25b2d10a)
- 
-![quiz with time](https://github.com/user-attachments/assets/bf07a157-afd7-46bd-8f8d-2a422e17496d)
-![Analysis of quiz](https://github.com/user-attachments/assets/5ece7d2a-71ff-41bd-8375-1a78a4523747)
- ![about](https://github.com/user-attachments/assets/02b6e184-16f6-4382-809d-45b4db74ff67)
- ![lessons creator](https://github.com/user-attachments/assets/82a24d49-aa7d-4e86-aa7d-564bf741d45c)
- [video mentors](https://github.com/user-attachments/assets/2623e585-7be0-4ea0-a25f-a30e97c1eb0d)
- [mentors](https://github.com/user-attachments/assets/9bea878a-f2dc-4523-8a9a-55140eed275b)

![automatic dout ask](https://github.com/user-attachments/assets/7b8c2886-82e0-4014-85a7-8da035e20224)

![automatic dout ask](https://github.com/user-attachments/assets/08ed6a25-5d83-444a-bbac-3007c3493510)
![user analysis](https://github.com/user-attachments/assets/66592ce7-9a1c-4a88-9ab6-29eec5191045)
![streak](https://github.com/user-attachments/assets/53a8d3db-40ba-44cc-a986-6a45f527f727)
![streak status](https://github.com/user-attachments/assets/ef651a71-5364-4790-93e0-b0039e8b0e52)
![emotion detection](https://github.com/user-attachments/assets/e3804c8e-f8bd-4a31-ab7d-ddc4e1cb7f9e)
![cam with emotions](https://github.com/user-attachments/assets/5bc9d307-d093-4e10-84cc-f2be4e7e1cbe)

![learning by quizzes](https://github.com/user-attachments/assets/86bfa73c-7a82-4d35-97a6-73818d5e7f37)

![math puzzeles](https://github.com/user-attachments/assets/480f41a8-1f41-4112-92c4-e51309254866)


![learning by games](https://github.com/user-attachments/assets/9c2393e7-225f-435b-b9ad-57bee8eec91e)
![learn topics](https://github.com/user-attachments/assets/c0cbeb20-84b9-4ee9-a4e2-adcb012d6460)

![generate quiz](https://github.com/user-attachments/assets/97c9f74e-f3ac-44f1-9d3b-86f2c18c28bd)
![general knowledge](https://github.com/user-attachments/assets/8f54a180-9d44-40ba-890d-7a6ce2308a71)



![correction of quiz](https://github.com/user-attachments/assets/51196624-49cf-40cb-ac84-a2a5469a146a)
![cerification and progress](https://github.com/user-attachments/assets/03ecef8b-799b-4641-9dfd-825deb5cd34b)


![word master](https://github.com/user-attachments/assets/f222b782-84d7-463a-995a-defa331baf92)

