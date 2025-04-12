from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
import logging
import json
import re

from .models import Lesson, Quiz, Question, Choice, UserLessonProgress, UserQuizAttempt, Subject, AIChat, ChatMessage
from core.utils import generate_quiz_for_topic, generate_content, generate_lesson_content

logger = logging.getLogger(__name__)

@login_required
def generate_content_view(request):
    """Generate content such as lessons, quizzes, etc."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST method is allowed'}, status=405)
    
    topic = request.POST.get('topic')
    content_type = request.POST.get('content_type')
    difficulty = request.POST.get('difficulty', 'medium')
    grade = request.user.profile.grade if hasattr(request.user, 'profile') else '5'
    
    if not topic:
        return JsonResponse({'status': 'error', 'message': 'Topic is required'}, status=400)
    
    if content_type == 'quiz':
        try:
            # Get the number of questions from the request, with better error handling
            try:
                question_count = int(request.POST.get('question_count', 10))
                # Ensure question count is within reasonable limits
                if question_count < 1:
                    question_count = 5  # Default to 5 if too small
                elif question_count > 30:
                    question_count = 30  # Cap at 30 to prevent excessive generation
            except (ValueError, TypeError):
                # Default to 10 questions if question_count is not a valid integer
                question_count = 10
                logger.warning(f"Invalid question_count provided: {request.POST.get('question_count')}, defaulting to {question_count}")
            
            # Generate the quiz content using the utility function
            try:
                quiz_data = generate_quiz_for_topic(topic, grade, 'en', question_count)
                
                # Verify quiz data
                if not isinstance(quiz_data, dict):
                    logger.error(f"Invalid quiz data format: {type(quiz_data)}")
                    quiz_data = {"quiz_title": f"Quiz on {topic}", "questions": []}
                
                if 'error' in quiz_data:
                    logger.error(f"Quiz generation returned error: {quiz_data['error']}")
                    # We'll continue with the quiz data anyway - fallback logic should have handled this
            except Exception as e:
                logger.error(f"Exception during quiz generation: {str(e)}")
                # Create a default quiz structure to avoid 500 error
                quiz_data = {"quiz_title": f"Quiz on {topic}", "questions": []}
            
            # Check if questions were generated
            questions_data = quiz_data.get('questions', [])
            if not questions_data:
                logger.warning("No questions were generated. Creating fallback quiz.")
                from core.utils import create_fallback_quiz
                quiz_data = create_fallback_quiz(topic, grade, question_count)
                questions_data = quiz_data.get('questions', [])
            
            # Calculate passing score based on number of questions
            # For example, if we have 10 questions, passing score could be 60%
            # If we have 5 questions, passing score could be 80%
            if question_count <= 5:
                passing_score = 80
            elif question_count <= 10:
                passing_score = 70
            elif question_count <= 15:
                passing_score = 65
            else:
                passing_score = 60
            
            # Create the quiz in the database
            with transaction.atomic():
                # Default values for required fields to avoid NULL constraint errors
                default_passing_score = 70
                
                quiz = Quiz.objects.create(
                    title=quiz_data.get('quiz_title', f'Quiz on {topic}'),
                    description=f'A {difficulty} difficulty quiz on {topic} for grade {grade}',
                    grade=grade,
                    # Ensure passing_score is always set and never null
                    passing_score=passing_score if passing_score is not None else default_passing_score,
                    time_limit=question_count * 2  # Roughly 2 minutes per question
                )
                
                # Try to find a relevant subject
                subject_keywords = topic.lower().split()
                subjects = Subject.objects.all()
                for subject in subjects:
                    if subject.name.lower() in topic.lower() or any(keyword in subject.name.lower() for keyword in subject_keywords):
                        quiz.subject = subject
                        quiz.save()
                        break
                
                # Track the actual number of questions created
                actual_question_count = 0
                
                # Create questions for the quiz
                for q_data in questions_data:
                    try:
                        # Get question text with fallback
                        question_text = q_data.get('question', f'Question about {topic}')
                        if not question_text or len(question_text.strip()) < 5:
                            question_text = f'Question about {topic}'
                        
                        # Create the question
                        question = Question.objects.create(
                            quiz=quiz,
                            question_text=question_text,
                            question_type='multiple_choice',
                            explanation=q_data.get('explanation', '')
                        )
                        
                        # Create choices for the question
                        options = q_data.get('options', ['Option A', 'Option B', 'Option C', 'Option D'])
                        # Ensure there are at least 4 options
                        while len(options) < 4:
                            options.append(f'Option {len(options) + 1}')
                        
                        correct_answer_index = q_data.get('correct_answer', 0)
                        # Validate correct_answer_index is within range
                        if not isinstance(correct_answer_index, int) or correct_answer_index < 0 or correct_answer_index >= len(options):
                            correct_answer_index = 0
                        
                        for i, option_text in enumerate(options):
                            # Ensure option text is valid
                            if not option_text or len(option_text.strip()) < 1:
                                option_text = f'Option {i+1}'
                                
                            Choice.objects.create(
                                question=question,
                                choice_text=option_text,
                                is_correct=(i == correct_answer_index)
                            )
                        
                        actual_question_count += 1
                    except Exception as e:
                        logger.error(f"Error creating question: {str(e)}")
                        # Continue with next question
                
                # If no questions were created, add at least one default question
                if actual_question_count == 0:
                    default_question = Question.objects.create(
                        quiz=quiz,
                        question_text=f"What is the main topic of this quiz?",
                        question_type='multiple_choice',
                        explanation=f"This quiz is about {topic}."
                    )
                    
                    for i, option in enumerate([topic, f"Not {topic}", "None of the above", "All of the above"]):
                        Choice.objects.create(
                            question=default_question,
                            choice_text=option,
                            is_correct=(i == 0)
                        )
                    
                    actual_question_count = 1
                
                # If the actual number of questions created differs from the requested count,
                # adjust the passing score accordingly
                if actual_question_count != question_count:
                    logger.info(f"Adjusting passing score for quiz {quiz.id}: requested {question_count} questions, created {actual_question_count}")
                    
                    if actual_question_count <= 5:
                        quiz.passing_score = 80
                    elif actual_question_count <= 10:
                        quiz.passing_score = 70
                    elif actual_question_count <= 15:
                        quiz.passing_score = 65
                    else:
                        quiz.passing_score = 60
                    
                    quiz.save()
                
                # Double-check that passing_score is set
                if quiz.passing_score is None or quiz.passing_score == 0:
                    quiz.passing_score = default_passing_score
                    quiz.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Quiz generated successfully',
                'redirect_url': reverse('tutor:quiz_detail', args=[quiz.id])
            })
        
        except ValueError as e:
            logger.error(f"ValueError during quiz generation: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': 'Failed to generate quiz. Please try again later.'
            }, status=400)
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            return JsonResponse({
                'status': 'error', 
                'message': 'Failed to generate quiz. Please try again later.'
            }, status=500)
    
    elif content_type == 'lesson':
        try:
            # Get parameters specific to lesson generation
            learning_style = request.POST.get('learning_style', 'unknown')
            
            # Check if we're creating content from direct JSON input
            content_json = request.POST.get('content_json')
            
            if content_json:
                # If direct JSON content is provided, use it instead of generating
                try:
                    # Validate JSON format
                    lesson_content = json.loads(content_json)
                    # Ensure it has the required structure
                    if not isinstance(lesson_content, list) or not all(isinstance(item, dict) for item in lesson_content):
                        raise ValueError("Invalid lesson content structure. Expected a list of section objects.")
                except json.JSONDecodeError:
                    return JsonResponse({'status': 'error', 'message': 'Invalid JSON format in content_json'}, status=400)
            else:
                # Generate lesson content using the utility function
                generated_text = generate_lesson_content(topic, grade, learning_style, 'en')
                
                # Check if there's an error in the response
                if generated_text.startswith('Error:'):
                    return JsonResponse({'status': 'error', 'message': generated_text}, status=500)
                
                # Try to create sections from the generated text
                lesson_sections = []
                
                # Split content into sections (introduction, main content, summary)
                paragraphs = generated_text.split('\n\n')
                
                # Create at least 3 sections: introduction, main content, practice
                if len(paragraphs) >= 3:
                    # Introduction section
                    lesson_sections.append({
                        "section_title": "Introduction to " + topic,
                        "section_content": '\n\n'.join(paragraphs[:2])
                    })
                    
                    # Main content section
                    lesson_sections.append({
                        "section_title": "Key Concepts about " + topic,
                        "section_content": '\n\n'.join(paragraphs[2:len(paragraphs)-2])
                    })
                    
                    # Practice section
                    lesson_sections.append({
                        "section_title": "Practice and Review",
                        "section_content": '\n\n'.join(paragraphs[len(paragraphs)-2:])
                    })
                else:
                    # Fallback for shorter content
                    lesson_sections.append({
                        "section_title": "Introduction to " + topic,
                        "section_content": paragraphs[0] if paragraphs else "Introduction to " + topic
                    })
                    
                    lesson_sections.append({
                        "section_title": "Key Concepts about " + topic,
                        "section_content": '\n\n'.join(paragraphs[1:]) if len(paragraphs) > 1 else "Key concepts about " + topic
                    })
                
                # Convert sections to JSON 
                lesson_content = lesson_sections
            
            # Create the lesson in the database
            with transaction.atomic():
                # Try to find a relevant subject
                subject_keywords = topic.lower().split()
                subject = None
                subjects = Subject.objects.all()
                
                for s in subjects:
                    if s.name.lower() in topic.lower() or any(keyword in s.name.lower() for keyword in subject_keywords):
                        subject = s
                        break
                
                # If no subject was found, use the first available subject or create a default one
                if subject is None:
                    # Try to get the first subject
                    subject = Subject.objects.first()
                    
                    # If no subjects exist, create a default one
                    if subject is None:
                        subject = Subject.objects.create(
                            name="General",
                            description="General knowledge and miscellaneous topics"
                        )
                
                # Create the lesson
                lesson = Lesson.objects.create(
                    subject=subject,
                    title=f"Lesson on {topic}",
                    description=f"A lesson about {topic} for grade {grade} students using {learning_style} learning style.",
                    content=json.dumps(lesson_content),
                    grade=grade,
                    difficulty=difficulty,
                    estimated_duration=20  # Default to 20 minutes
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Lesson generated successfully',
                'redirect_url': reverse('tutor:lesson_detail', args=[lesson.id])
            })
            
        except Exception as e:
            logger.error(f"Error generating lesson: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Failed to generate lesson: {str(e)}'}, status=500)
    
    else:
        return JsonResponse({'status': 'error', 'message': f'Content type {content_type} not supported'}, status=400)

@login_required
def lesson_detail(request, lesson_id):
    """View a specific lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Create or get user progress for this lesson
    progress, created = UserLessonProgress.objects.get_or_create(
        user=request.user.profile,
        lesson=lesson,
        defaults={'progress_percentage': 0, 'completed': False}
    )
    
    # Parse lesson content to extract sections
    lesson_sections = []
    try:
        if lesson.content:
            # Parse content as JSON if it's a string
            if isinstance(lesson.content, str):
                try:
                    content_data = json.loads(lesson.content)
                    
                    # Process each section from JSON and add a unique ID
                    if len(content_data) < 10:
                        # If we have fewer than 10 sections, expand to more detailed sections
                        expanded_sections = []
                        
                        # Main topics to create sections for - 10 sections total
                        section_topics = [
                            {"title": "Introduction", "prefix": "Introduction to"},
                            {"title": "Key Concepts", "prefix": "Key Concepts of"},
                            {"title": "Historical Context", "prefix": "Historical Background of"},
                            {"title": "Foundational Principles", "prefix": "Foundational Principles of"},
                            {"title": "Practical Applications", "prefix": "Real-world Applications of"},
                            {"title": "Examples and Demonstrations", "prefix": "Examples and Demonstrations of"},
                            {"title": "Advanced Topics", "prefix": "Advanced Topics in"},
                            {"title": "Related Fields", "prefix": f"How This Relates to Other Fields"},
                            {"title": "Recent Developments", "prefix": f"Recent Developments in"},
                            {"title": "Practice and Review", "prefix": "Practice and Review for"}
                        ]
                        
                        # Generate sections from main content by splitting it
                        main_content = ""
                        for section in content_data:
                            if "Key Concepts" in section.get('section_title', ''):
                                main_content = section.get('section_content', '')
                                break
                        
                        # If we have main content, split it into paragraphs
                        if main_content:
                            paragraphs = main_content.split('\n\n')
                            
                            # Determine how many paragraphs to allocate per new section
                            total_paragraphs = len(paragraphs)
                            paragraphs_per_section = max(1, total_paragraphs // (len(section_topics) - 2))
                            
                            # Keep introduction and practice as originally defined
                            for section in content_data:
                                if "Introduction" in section.get('section_title', ''):
                                    expanded_sections.append({
                                        "section_title": section_topics[0]["title"] + " " + lesson.title.replace("Lesson on ", ""),
                                        "section_content": section.get('section_content', '')
                                    })
                                    break
                            
                            # Create middle sections from the main content
                            for i in range(1, len(section_topics) - 1):
                                if i * paragraphs_per_section < total_paragraphs:
                                    section_paragraphs = paragraphs[
                                        (i-1) * paragraphs_per_section:
                                        min(i * paragraphs_per_section, total_paragraphs)
                                    ]
                                    
                                    # Clean the content - remove asterisks that might be markdown formatting
                                    section_content = '\n\n'.join(section_paragraphs)
                                    section_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', section_content)  # Remove bold asterisks
                                    section_content = re.sub(r'\*([^*]+)\*', r'\1', section_content)      # Remove italic asterisks
                                    
                                    expanded_sections.append({
                                        "section_title": section_topics[i]["prefix"] + " " + lesson.title.replace("Lesson on ", ""),
                                        "section_content": section_content
                                    })
                            
                            # Add practice section
                            for section in content_data:
                                if "Practice" in section.get('section_title', ''):
                                    expanded_sections.append({
                                        "section_title": section_topics[-1]["title"],
                                        "section_content": section.get('section_content', '')
                                    })
                                    break
                            
                            # Use expanded sections instead of original
                            content_data = expanded_sections
                    
                    # Process all sections
                    for i, section in enumerate(content_data):
                        section_id = f"section-{i+1}"
                        title = section.get('section_title', f'Section {i+1}')
                        content = section.get('section_content', '')
                        
                        # Clean the content - remove asterisks that might be markdown formatting
                        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)  # Remove bold asterisks
                        content = re.sub(r'\*([^*]+)\*', r'\1', content)      # Remove italic asterisks
                        
                        # Ensure content is not placeholder text
                        if "this section" in content.lower() and "concepts" in content.lower() and len(content) < 200:
                            # This appears to be placeholder text, replace with more specific content
                            if "introduction" in title.lower():
                                content = f"""Welcome to this lesson about {lesson.title}! In this introduction, we'll explore the basic concepts and why it's important to learn.

{lesson.title} is an important subject for grade {lesson.grade} students because it helps build foundational knowledge in this area. Throughout this lesson, you'll learn key facts, concepts, and applications.

Let's start by understanding what {lesson.title} is and why we study it. This lesson will cover the main ideas, provide examples, and help you practice what you've learned."""
                            elif "key concept" in title.lower() or "main concept" in title.lower():
                                content = f"""Now that we've introduced {lesson.title}, let's explore some of the key concepts in more detail.

When studying {lesson.title}, there are several important ideas to understand:

1. The basic principles and foundations
2. How it relates to other subjects you're learning
3. Real-world applications
4. Historical development and context

Each of these aspects helps us understand {lesson.title} more deeply. As you learn more, you'll see connections between these concepts and how they work together."""
                            elif "practice" in title.lower() or "review" in title.lower():
                                content = f"""Let's practice what we've learned about {lesson.title}. Here are some questions and activities to help you review:

Reflection Questions:
1. What is {lesson.title} and why is it important?
2. How does it connect to other things you've learned?
3. Can you think of examples in everyday life?

Practice Activities:
1. Create a mind map showing the key concepts
2. Explain what you've learned to a friend or family member
3. Find examples in books or online articles

Remember, practicing helps reinforce what you've learned."""
                        
                        lesson_sections.append({
                            'id': section_id,
                            'title': title,
                            'content': content.replace('\n', '<br>'),
                        })
                except json.JSONDecodeError:
                    # If not valid JSON, use the content as a single section
                    logger.warning(f"Failed to parse lesson content as JSON for lesson {lesson_id}")
                    lesson_sections = [{
                        'id': 'section-1',
                        'title': 'Content',
                        'content': str(lesson.content).replace('\n', '<br>'),
                    }]
        if not lesson_sections:
            # If no sections were created, create a default one
            lesson_sections = [{
                'id': 'section-1',
                'title': 'Lesson Content',
                'content': f"This lesson about {lesson.title} is designed for Grade {lesson.grade} students.".replace('\n', '<br>'),
            }]
    except Exception as e:
        logger.error(f"Error processing lesson content: {str(e)}")
        lesson_sections = [{
            'id': 'section-1',
            'title': 'Content',
            'content': f"There was an error loading the lesson content. Please try refreshing the page. Error: {str(e)}".replace('\n', '<br>'),
        }]
    
    # Handle lesson completion
    if request.method == 'POST' and 'complete_lesson' in request.POST:
        progress.completed = True
        progress.progress_percentage = 100
        progress.save()
        messages.success(request, _("Lesson marked as completed!"))
        return redirect('tutor:lesson_detail', lesson_id=lesson.id)
    
    # Handle progress update via AJAX
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            progress_value = data.get('progress_percentage')
            if progress_value is not None:
                try:
                    progress_value = int(progress_value)
                    progress.progress_percentage = max(progress.progress_percentage, progress_value)
                    if progress_value >= 95:
                        progress.completed = True
                    progress.save()
                    return JsonResponse({'status': 'success'})
                except ValueError:
                    return JsonResponse({'status': 'error', 'message': 'Invalid progress value'}, status=400)
            return JsonResponse({'status': 'error', 'message': 'No progress value provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    
    # Get related quizzes - from both direct relation and subject relation
    related_quizzes = Quiz.objects.filter(
        Q(lesson=lesson) | Q(subject=lesson.subject)
    ).distinct()
    
    context = {
        'title': lesson.title,
        'lesson': lesson,
        'progress': progress,
        'lesson_sections': lesson_sections,
        'quizzes': related_quizzes
    }
    return render(request, 'tutor/lesson_detail.html', context)

@login_required
def quizzes(request):
    """View all quizzes"""
    quizzes = Quiz.objects.all().order_by('-created_at')
    
    context = {
        'title': 'Quizzes',
        'quizzes': quizzes
    }
    return render(request, 'tutor/quizzes.html', context)

@login_required
def quiz_detail(request, quiz_id):
    """View a specific quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Get questions with choices
    questions = quiz.questions.all()
    question_count = questions.count()
    
    # If the quiz has no questions, create a fix button for admins/teachers
    fix_quiz_url = None
    if question_count == 0 and request.user.is_staff:
        fix_quiz_url = reverse('tutor:fix_empty_quiz', args=[quiz.id])
    
    # Prepare questions with their choices for the template
    questions_with_choices = []
    for question in questions:
        questions_with_choices.append({
            'question': question,
            'choices': question.choices.all()
        })
    
    context = {
        'title': quiz.title,
        'quiz': quiz,
        'questions_with_choices': questions_with_choices,
        'question_count': question_count,
        'fix_quiz_url': fix_quiz_url
    }
    return render(request, 'tutor/quiz_detail.html', context)

@login_required
def fix_empty_quiz(request, quiz_id):
    """Generate questions for an empty quiz"""
    if not request.user.is_staff:
        messages.error(request, _("You don't have permission to fix quizzes."))
        return redirect('tutor:quiz_detail', quiz_id=quiz_id)
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if quiz already has questions
    if quiz.questions.count() > 0:
        messages.info(request, _("This quiz already has questions."))
        return redirect('tutor:quiz_detail', quiz_id=quiz_id)
    
    try:
        with transaction.atomic():
            # Determine number of questions based on quiz time limit
            question_count = max(5, min(quiz.time_limit // 2, 10))
            
            # Generate quiz content based on the quiz title
            topic = quiz.title.replace('Quiz on ', '')
            grade = quiz.grade if quiz.grade else '5'
            
            # Call the quiz generation function
            from core.utils import generate_quiz_for_topic, create_fallback_quiz
            try:
                quiz_data = generate_quiz_for_topic(topic, grade, 'en', question_count)
            
                # Verify quiz data
                if not isinstance(quiz_data, dict):
                    logger.error(f"Invalid quiz data format: {type(quiz_data)}")
                    quiz_data = create_fallback_quiz(topic, grade, question_count)
                
                if 'error' in quiz_data:
                    logger.error(f"Quiz generation returned error: {quiz_data['error']}")
                    quiz_data = create_fallback_quiz(topic, grade, question_count)
            except Exception as e:
                logger.error(f"Exception during quiz generation: {str(e)}")
                quiz_data = create_fallback_quiz(topic, grade, question_count)
            
            # Check if we have questions
            questions_data = quiz_data.get('questions', [])
            if not questions_data:
                logger.warning("No questions were generated. Creating fallback quiz.")
                quiz_data = create_fallback_quiz(topic, grade, question_count)
                questions_data = quiz_data.get('questions', [])
            
            # Create questions from the generated content
            actual_question_count = 0
            
            for q_data in questions_data:
                try:
                    # Get question text with fallback
                    question_text = q_data.get('question', f'Question about {topic}')
                    if not question_text or len(question_text.strip()) < 5:
                        question_text = f'Question about {topic}'
                    
                    # Create the question
                    question = Question.objects.create(
                        quiz=quiz,
                        question_text=question_text,
                        question_type='multiple_choice',
                        explanation=q_data.get('explanation', '')
                    )
                    
                    # Create choices for the question
                    options = q_data.get('options', ['Option A', 'Option B', 'Option C', 'Option D'])
                    # Ensure there are at least 4 options
                    while len(options) < 4:
                        options.append(f'Option {len(options) + 1}')
                    
                    correct_answer_index = q_data.get('correct_answer', 0)
                    # Validate correct_answer_index is within range
                    if not isinstance(correct_answer_index, int) or correct_answer_index < 0 or correct_answer_index >= len(options):
                        correct_answer_index = 0
                    
                    for i, option_text in enumerate(options):
                        # Ensure option text is valid
                        if not option_text or len(option_text.strip()) < 1:
                            option_text = f'Option {i+1}'
                            
                        Choice.objects.create(
                            question=question,
                            choice_text=option_text,
                            is_correct=(i == correct_answer_index)
                        )
                    
                    actual_question_count += 1
                except Exception as e:
                    logger.error(f"Error creating question during fix_empty_quiz: {str(e)}")
                    # Continue with next question
            
            # If no questions were created at all, add a default question
            if actual_question_count == 0:
                default_question = Question.objects.create(
                    quiz=quiz,
                    question_text=f"What is the main topic of this quiz?",
                    question_type='multiple_choice',
                    explanation=f"This quiz is about {topic}."
                )
                
                for i, option in enumerate([topic, f"Not {topic}", "None of the above", "All of the above"]):
                    Choice.objects.create(
                        question=default_question,
                        choice_text=option,
                        is_correct=(i == 0)
                    )
            
            messages.success(request, _("Successfully generated questions for this quiz!"))
        
    except Exception as e:
        logger.error(f"Error fixing quiz {quiz_id}: {str(e)}")
        messages.error(request, _("Failed to generate questions. Please try again later."))
    
    return redirect('tutor:quiz_detail', quiz_id=quiz_id)

@login_required
def tutor_home(request):
    """Home page for the tutor module"""
    return render(request, 'tutor/home.html', {'title': 'Learning Hub'})

@login_required
def ai_chat(request):
    """Chat with AI tutor"""
    # Get user profile
    user_profile = request.user.profile if hasattr(request.user, 'profile') else None
    
    # Get current chat if chat_id is provided
    chat_id = request.GET.get('chat_id')
    subject_id = request.GET.get('subject_id')
    chat = None
    
    # Initialize chat from chat_id or subject_id
    if chat_id:
        chat = get_object_or_404(AIChat, id=chat_id, user=user_profile)
    elif subject_id:
        subject = get_object_or_404(Subject, id=subject_id)
        # Create new chat with the selected subject
        chat = AIChat.objects.create(
            user=user_profile,
            subject=subject,
            title=f"Chat about {subject.name}"
        )
    
    # Get or create a default chat if none exists
    if not chat and user_profile:
        # Check if user has any chats
        chats = AIChat.objects.filter(user=user_profile)
        if chats.exists():
            chat = chats.latest('updated_at')
        else:
            # Create a default chat
            chat = AIChat.objects.create(
                user=user_profile,
                title="New Conversation"
            )
    
    # Handle POST request (chat message)
    if request.method == 'POST' and chat:
        message_text = request.POST.get('message', '').strip()
        detected_language = request.POST.get('detected_language', 'en-US')
        language_code = detected_language.split('-')[0] if '-' in detected_language else detected_language
        
        if message_text:
            # Save user message
            user_message = ChatMessage.objects.create(
                chat=chat,
                message_type='user',
                content=message_text,
                language=language_code
            )
            
            # Process the message and generate AI response
            try:
                # Update chat timestamp
                chat.save()  # This will update the updated_at field
                
                # Use the generate_content utility to get AI response
                from core.utils import generate_content
                
                # Build prompt based on chat context
                context = []
                # Get last 10 messages for context (excluding the one we just added)
                previous_messages = ChatMessage.objects.filter(chat=chat).order_by('-timestamp')[:11]
                for prev_message in reversed(previous_messages):
                    if prev_message.id != user_message.id:
                        role = "user" if prev_message.message_type == "user" else "assistant"
                        context.append(f"{role}: {prev_message.content}")
                
                # Create prompt with context
                if chat.subject:
                    subject_prompt = f"You are an AI tutor specializing in {chat.subject.name}. "
                else:
                    subject_prompt = "You are an AI tutor helping a student. "
                
                prompt = f"{subject_prompt}Answer the user's question concisely and helpfully. "
                prompt += "If the response is educational, provide accurate information, explain concepts clearly, and use examples when helpful.\n\n"
                
                # Add conversation context if available
                if context:
                    prompt += "Here's the previous conversation:\n"
                    prompt += "\n".join(context[-8:])  # Use up to 8 most recent messages for context
                    prompt += f"\n\nuser: {message_text}\nassistant: "
                else:
                    prompt += f"user: {message_text}\nassistant: "
                
                # Generate AI response
                response = generate_content(prompt, language_code)
                
                # Check for errors in the response
                if isinstance(response, dict) and "error" in response:
                    error_message = response.get("error", "Unknown error processing your request")
                    ai_response_text = f"I'm sorry, I encountered an issue. {error_message} Please try again."
                else:
                    # Extract text from the Gemini API response
                    ai_response_text = ""
                    
                    # Try to extract from different response formats
                    if isinstance(response, dict):
                        if "candidates" in response and response["candidates"]:
                            candidate = response["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                for part in candidate["content"]["parts"]:
                                    if "text" in part:
                                        ai_response_text += part["text"]
                                        
                    # If extraction failed, provide a default message
                    if not ai_response_text:
                        ai_response_text = "I received your message, but I'm having trouble generating a response right now. Please try again."
                
                # Save AI response
                ai_message = ChatMessage.objects.create(
                    chat=chat,
                    message_type='ai',
                    content=ai_response_text,
                    language=language_code
                )
                
                # Update chat title for new chats
                if chat.title == "New Conversation" and ChatMessage.objects.filter(chat=chat).count() <= 3:
                    new_title = message_text[:50] + "..." if len(message_text) > 50 else message_text
                    chat.title = new_title
                    chat.save()
                
                # Return JSON response for AJAX requests
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'ai_message': ai_response_text,
                        'language': language_code,
                        'chat_title': chat.title
                    })
                
            except Exception as e:
                logger.error(f"Error in chat processing: {str(e)}")
                
                # Return error response for AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'error': "There was an error processing your message. Please try again.",
                    }, status=500)
    
    # Get all chats for the sidebar
    all_chats = []
    if user_profile:
        all_chats = AIChat.objects.filter(user=user_profile).order_by('-updated_at')
    
    # Get chat messages
    chat_messages = []
    if chat:
        chat_messages = chat.messages.all().order_by('timestamp')
    
    # Get subjects for the sidebar
    subjects = Subject.objects.all()
    
    context = {
        'title': 'AI Chat',
        'chat': chat,
        'messages': chat_messages,
        'all_chats': all_chats,
        'subjects': subjects
    }
    
    return render(request, 'tutor/chat.html', context)

@login_required
def lessons(request):
    """View all lessons"""
    lessons = Lesson.objects.all().order_by('-created_at')
    
    context = {
        'title': 'Lessons',
        'lessons': lessons
    }
    return render(request, 'tutor/lessons.html', context)

@login_required
def subjects(request):
    """View all subjects"""
    subjects = Subject.objects.all()
    
    context = {
        'title': 'Subjects',
        'subjects': subjects
    }
    return render(request, 'tutor/subjects.html', context)

@login_required
def subject_lessons(request, subject_id):
    """View lessons for a specific subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    lessons = Lesson.objects.filter(subject=subject).order_by('-created_at')
    
    context = {
        'title': f'{subject.name} Lessons',
        'subject': subject,
        'lessons': lessons
    }
    return render(request, 'tutor/subject_lessons.html', context)

@login_required
def subject_quizzes(request, subject_id):
    """View quizzes for a specific subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    quizzes = Quiz.objects.filter(subject=subject).order_by('-created_at')
    
    # Get user quiz attempts and attach them to the quizzes
    user_quiz_attempts = {}
    if hasattr(request.user, 'profile'):
        # Get all user attempts for quizzes in this subject
        attempts = UserQuizAttempt.objects.filter(
            user=request.user.profile,
            quiz__subject=subject
        ).select_related('quiz')
        
        # Create a dictionary of quiz_id -> attempt for easy lookup in template
        for attempt in attempts:
            user_quiz_attempts[attempt.quiz_id] = attempt
    
    # Prepare quizzes with attempt information
    quizzes_with_attempts = []
    for quiz in quizzes:
        # Add question count property
        quiz.question_count = quiz.questions.count()
        # Add grade level for display
        quiz.grade_level = quiz.grade
        # Add attempt if it exists
        quiz.user_attempt = user_quiz_attempts.get(quiz.id)
        quiz.has_attempt = quiz.id in user_quiz_attempts
        
        if quiz.has_attempt:
            attempt = user_quiz_attempts[quiz.id]
            quiz.score_percentage = int((attempt.score / attempt.max_score) * 100) if attempt.max_score > 0 else 0
            quiz.last_attempt_date = attempt.date_attempted
            
        quizzes_with_attempts.append(quiz)
    
    context = {
        'title': f'{subject.name} Quizzes',
        'subject': subject,
        'quizzes': quizzes_with_attempts
    }
    return render(request, 'tutor/subject_quizzes.html', context)

@login_required
def delete_quiz(request, quiz_id):
    """Delete a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if this is a POST request (actual deletion)
    if request.method == 'POST':
        # Store subject ID for redirect if the quiz is linked to a subject
        subject_id = quiz.subject.id if quiz.subject else None
        
        # Delete the quiz
        quiz.delete()
        
        # Set success message
        messages.success(request, _('Quiz deleted successfully.'))
        
        # Redirect based on context
        if subject_id and request.GET.get('from') == 'subject':
            return redirect('tutor:subject_quizzes', subject_id=subject_id)
        else:
            return redirect('tutor:quizzes')
    
    # For GET requests, show confirmation page or handle via JavaScript
    return JsonResponse({
        'status': 'error',
        'message': 'Delete requests must use POST method'
    }, status=405)

@login_required
def delete_lesson(request, lesson_id):
    """Delete a lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check if this is a POST request (actual deletion)
    if request.method == 'POST':
        # Store subject ID for redirect if the lesson is linked to a subject
        subject_id = lesson.subject.id if lesson.subject else None
        
        # Delete the lesson
        lesson.delete()
        
        # Set success message
        messages.success(request, _('Lesson deleted successfully.'))
        
        # Redirect based on context
        if subject_id and request.GET.get('from') == 'subject':
            return redirect('tutor:subject_lessons', subject_id=subject_id)
        else:
            return redirect('tutor:lessons')
    
    # For GET requests, show confirmation page or handle via JavaScript
    return JsonResponse({
        'status': 'error',
        'message': 'Delete requests must use POST method'
    }, status=405)