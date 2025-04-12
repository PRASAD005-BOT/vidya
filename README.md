# VidyAI++ - Multilingual AI Tutoring & Mentorship Platform

## Selected Domain
Education Technology (EdTech) focusing on accessibility and personalized learning
![home page](https://github.com/user-attachments/assets/cb30df60-498c-49a7-b2b8-9580fb7227bf)

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

This project is licens![dashboard2](https://github.com/user-attachments/assets/3765befe-060d-4dca-be62-e0037396c01b)
ed under the MIT Licen![multilang](https://github.com/user-attachments/assets/dfaa![mult![generate quiz](https://github.com/user-attachments/assets/f3f79![math puzzeles](https://github.com/user-attachments/assets/52d8acf4-7f62-49d8-912e-c2606dedb214)
b7a-8dfd-![Analysis of![streak status](https://github.com/user-attachments/assets/c3f2f55a-10b4-4abe-8d02-b82dd7cb3e66)
 quiz](https://github.com/user-a![streak](https://github.com/user-attachments/assets/d701f0cd-01c5![user analysis](https://github.com/user-attachments/assets/fa3d04bf-5ca6-48de-a74b-2b66d0fcd956)
-4cea-9842-f72c47ecfba6)
tt![cam w![cerification and progress](https://github.com/user-attachme![Quiz](https://github.com/user-attachments/assets/0cc249c9-40c9-47b5-8de6-485e06c15b9f)
nts/assets/4f4bd0c0-c635-4061-9448-7e48f2c93489)
ith emotions](https://github.com/user-attachments/assets/3fb83905-614c-463b-9ffa-734795871410)![learning by quizzes](https://github.com/user-attachments/assets/f64eb92d-2d4f-444b![word master](https://github.com/user-attachments/assets/6c466394-e9ff-4f88-b871-c43fe925fef8)
-80a1-3445faad6f75)

achments/assets/1a6d85fc-d897-41cb-a856![emotion detection](https://github.com/user-att![v![learning by games](https://github.com/user-attachments/assets/82c1da99-1f04-4a9e-babe-8829ce027736)
ideo mentors](https://github.com/user-attachments/assets/bd0d1ce6-926a-423f-a8c3-7d69a3a58489)
ac![about](https://github.com/user-attachments/assets/2c86a91f-bafe-4a35-b27c-e8874639d4e8)
hments/assets/f0620167-![mentors](https://github.com/user-attachments/assets/1dae96b6-ebb7-45a5-b99f-75b5a2787bf4)
0dd7-4ff6-a545-c16e29b0b76a)
-5fd44f989a0b)
412b-8c4b-209f92db3311)
i lang](https://github.![mentors](ht![automatic dout ask](https://github.com/user-attachments/assets/3cc17f0c-09a1-42fd-ac94-fb60acfba4c6)
tps://github.com/user-attachments/assets/6f14f6e5-72ea-4940-a017-a51093c652ca)
com/user-attachments/assets/3c4d350d-0c19-4acd-9854-240413cc90b0![learn topics](https://github.com/user-attachments/assets/a333b41b-4d14-4bf6-8c08-388c583d5104)
)![lessons creator](https://github.com/user-attachments/assets/c50bc25b-d8a3-4c41-99bb-62409a8f9dfd)

cd11-d54b-48b2-8956-e92f060![correction of quiz](https://github.com/user-attachments/assets/9ffdbd7a-bd4f-48dc-b309-f9db385c50a5)
de750)
se - see the LICENSE![voice sppech mutlilanguage](https://github.com/user-attachments/assets/e5bfacff-a5a1-4df8-9e2a-36f9ca6c65e5)
 file for details.

## Acknowledgements![quiz with time](https://github.com/user-attachments/assets/2eb0cd7e![Quiz](https://github.com/user-attachments/assets/aaa794e9-0ced-411c-9a88-9f069b176289)
-62d8-4d30-82af-4f8bd105d93b)

![night visoin dark ![dashboard](https://github.com/user-attachments/assets/ae715da1-9789-4c78-8c05-c8a40d6b4817)
mode](https://github.com/user-attachments/assets/ed24d5![profile update](https://github.com/user-attachments/assets/6235133f-a489-4cdf-81ad-5b7ab18fcdfd)
f0-7ad2-4386-b33d-9876aae08148)

- Google Gemini API for AI capabilities
- National Education Policy (NEP) for educational framework guidance
- Django for the robust web framework
- Bootstrap for the responsive design components 
