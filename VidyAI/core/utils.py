import requests
import json
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)

def generate_content(prompt, language='en', max_tokens=1024):
    """
    Generate content using the Gemini API
    
    Args:
        prompt (str): The prompt to send to the Gemini API
        language (str): The language code for the response
        max_tokens (int): Maximum tokens to generate
        
    Returns:
        dict: Response from the Gemini API or error message
    """
    url = f"{settings.GEMINI_API_URL}?key={settings.GEMINI_API_KEY}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Customize the prompt based on language if not English
    if language != 'en':
        prompt = f"Please respond in {get_language_name(language)}. {prompt}"
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": max_tokens,
            "stopSequences": []
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    }
    
    try:
        # Add timeout to prevent hanging requests - 60 second timeout for larger content
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
        
        # Check for specific error codes
        if response.status_code == 400:
            error_data = response.json() if response.text else {"error": "Bad request"}
            error_message = error_data.get("error", {}).get("message", "Unknown API error")
            return {"error": f"API Error (400): {error_message}"}
        elif response.status_code == 429:
            return {"error": "Rate limit exceeded. Please try again later."}
        elif response.status_code == 403:
            return {"error": "API access forbidden. Please check your API key."}
        elif response.status_code == 500:
            return {"error": "Server error from Gemini API. Please try again later."}
        elif response.status_code == 502 or response.status_code == 503 or response.status_code == 504:
            return {"error": "Gemini API is temporarily unavailable. Please try again later."}
        
        # Raise for other error status codes
        response.raise_for_status()
        
        # Parse the JSON response
        try:
            result = response.json()
            # Check if result has expected structure
            if "candidates" not in result or not result["candidates"]:
                if "promptFeedback" in result and result["promptFeedback"].get("blockReason"):
                    return {"error": f"Content blocked: {result['promptFeedback'].get('blockReasonMessage', 'Unknown safety issue')}"}
                return {"error": "API returned empty response"}
            return result
        except json.JSONDecodeError:
            return {"error": "Failed to parse API response as JSON"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The operation took too long to complete."}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection issue. Please check your internet and try again."}
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') and hasattr(e.response, 'status_code') else "unknown"
        return {"error": f"HTTP error {status_code}: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def get_language_name(language_code):
    """
    Convert language code to language name
    
    Args:
        language_code (str): Two-letter language code
        
    Returns:
        str: Language name
    """
    language_map = {
        'en': 'English',
        'hi': 'Hindi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'bn': 'Bengali',
        'mr': 'Marathi',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'pa': 'Punjabi',
        'or': 'Odia'
    }
    return language_map.get(language_code, 'English')

def extract_text_from_gemini_response(response):
    """
    Extract text from Gemini API response
    
    Args:
        response (dict): Response from the Gemini API
        
    Returns:
        str: Extracted text or error message
    """
    # If the response is an error message, return it
    if isinstance(response, dict) and "error" in response:
        return f"Error: {response['error']}"
    
    try:
        # Handle the normal response structure
        if isinstance(response, dict) and "candidates" in response and response["candidates"]:
            try:
                candidate = response["candidates"][0]
                if "content" in candidate:
                    content = candidate["content"]
                    if "parts" in content:
                        parts = content["parts"]
                        text = ""
                        for part in parts:
                            if "text" in part:
                                text += part["text"]
                        return text
            except (KeyError, IndexError) as e:
                return f"Error: Could not extract text from response: {str(e)}"
        
        # Try alternative formats
        # For simple string responses
        if isinstance(response, str):
            return response
            
        # For dictionary with direct text
        if isinstance(response, dict) and "text" in response:
            return response["text"]
            
        # For dictionary with content field
        if isinstance(response, dict) and "content" in response:
            if isinstance(response["content"], str):
                return response["content"]
            elif isinstance(response["content"], dict) and "text" in response["content"]:
                return response["content"]["text"]
        
        # If we can't extract text, return an error message
        return "Error: Unsupported response format"
        
    except Exception as e:
        return f"Error: Failed to extract text: {str(e)}"

def generate_quiz_for_topic(topic, grade, language='en', num_questions=5):
    """
    Generate a quiz for a specific topic and grade level
    
    Args:
        topic (str): The topic for the quiz
        grade (str): The grade level
        language (str): Language code
        num_questions (int): Number of questions to generate
        
    Returns:
        dict: Quiz data with questions and answers
    """
    prompt = f"""
    Create a quiz on {topic} suitable for grade {grade} students. 
    The quiz MUST have EXACTLY {num_questions} multiple-choice questions.
    For each question, provide 4 options and mark the correct answer.
    Format your response as JSON with the following structure:
    
    {{
        "quiz_title": "Quiz title here",
        "questions": [
            {{
                "question": "Question text here",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Explanation for the correct answer"
            }}
        ]
    }}
    
    IMPORTANT: You MUST generate EXACTLY {num_questions} questions.
    Remember that the correct_answer is the index (0-3) of the correct option.
    """
    
    try:
        response = generate_content(prompt, language)
        generated_text = extract_text_from_gemini_response(response)
        
        # Extract JSON from the response
        try:
            # Find JSON in the text if it's wrapped in other content
            start_idx = generated_text.find('{')
            end_idx = generated_text.rfind('}') + 1
            json_str = generated_text[start_idx:end_idx]
            
            quiz_data = json.loads(json_str)
            return quiz_data
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse quiz data: {str(e)}")
            logger.info("Falling back to hardcoded quiz")
            return create_fallback_quiz(topic, grade, num_questions)
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        return create_fallback_quiz(topic, grade, num_questions)

def create_fallback_quiz(topic, grade, num_questions=5):
    """
    Create a fallback quiz when the API fails
    
    Args:
        topic (str): The topic for the quiz
        grade (str): The grade level
        num_questions (int): Number of questions to generate
        
    Returns:
        dict: Quiz data with questions and answers
    """
    # Ensure we don't exceed the number of fallback questions we have
    num_questions = min(num_questions, 10)
    
    # Create a quiz title based on the topic
    quiz_title = f"Quiz on {topic} for Grade {grade}"
    
    # Fallback questions - general knowledge that can be adapted to any topic
    fallback_questions = [
        {
            "question": f"What is the primary focus of studying {topic}?",
            "options": [
                f"Understanding basic concepts of {topic}",
                f"Memorizing facts about {topic}",
                f"Creating new theories about {topic}",
                f"Challenging existing ideas about {topic}"
            ],
            "correct_answer": 0,
            "explanation": f"The primary focus is to develop a fundamental understanding of {topic}."
        },
        {
            "question": f"Which of the following best describes {topic}?",
            "options": [
                f"A scientific discipline",
                f"An artistic expression",
                f"A mathematical concept",
                f"A philosophical idea"
            ],
            "correct_answer": 0,
            "explanation": f"{topic} is commonly classified as a scientific discipline, though it may have aspects of other fields."
        },
        {
            "question": f"When did the study of {topic} first begin?",
            "options": [
                "Ancient times",
                "Middle Ages",
                "19th century",
                "20th century"
            ],
            "correct_answer": 0,
            "explanation": f"Many aspects of {topic} have been studied since ancient times, though modern approaches developed later."
        },
        {
            "question": f"Who is generally credited with making significant early contributions to {topic}?",
            "options": [
                "Ancient Greek philosophers",
                "Renaissance scientists",
                "Modern researchers",
                "All of the above"
            ],
            "correct_answer": 3,
            "explanation": f"Knowledge about {topic} has been developed by thinkers throughout history."
        },
        {
            "question": f"Which field is most closely related to {topic}?",
            "options": [
                "Mathematics",
                "Science",
                "History",
                "It depends on the specific aspect of the topic"
            ],
            "correct_answer": 3,
            "explanation": f"{topic} likely has connections to multiple fields, depending on which aspects are being studied."
        },
        {
            "question": f"What is a common application of knowledge about {topic}?",
            "options": [
                "Solving real-world problems",
                "Academic research",
                "Educational purposes",
                "All of the above"
            ],
            "correct_answer": 3,
            "explanation": f"Knowledge about {topic} can be applied in many ways, including all of the options listed."
        },
        {
            "question": f"Which of the following would be a good way to learn more about {topic}?",
            "options": [
                "Reading textbooks",
                "Conducting experiments",
                "Talking to experts",
                "All of the above"
            ],
            "correct_answer": 3,
            "explanation": "A combination of different learning methods is usually most effective."
        },
        {
            "question": f"What skill is most important when studying {topic}?",
            "options": [
                "Critical thinking",
                "Memorization",
                "Creativity",
                "Mathematical ability"
            ],
            "correct_answer": 0,
            "explanation": "Critical thinking is essential for understanding and applying concepts in any field."
        },
        {
            "question": f"How has our understanding of {topic} changed over time?",
            "options": [
                "It has remained mostly the same",
                "It has evolved with new discoveries",
                "It has been completely revolutionized",
                "It has become less important"
            ],
            "correct_answer": 1,
            "explanation": "Knowledge in most fields evolves gradually as new discoveries are made."
        },
        {
            "question": f"What is the best approach to studying {topic}?",
            "options": [
                "Memorizing key facts",
                "Understanding underlying principles",
                "Practicing application",
                "A balanced approach including all of these"
            ],
            "correct_answer": 3,
            "explanation": "A balanced approach that includes understanding concepts and applying them is usually most effective."
        }
    ]
    
    # Return the quiz data
    return {
        "quiz_title": quiz_title,
        "questions": fallback_questions[:num_questions]
    }

def generate_lesson_content(topic, grade, learning_style, language='en'):
    """
    Generate lesson content tailored to a specific learning style
    
    Args:
        topic (str): The lesson topic
        grade (str): Grade level
        learning_style (str): Learning style (visual, auditory, kinesthetic)
        language (str): Language code
        
    Returns:
        str: Generated lesson content
    """
    style_prompts = {
        'visual': "Include diagrams, charts, and visual descriptions. Use bullet points and organize information visually. Use PLAIN TEXT without markdown formatting (no asterisks for emphasis).",
        'auditory': "Include dialogues, discussions, and content that can be read aloud. Use rhythm and patterns in explanations. Use PLAIN TEXT without markdown formatting (no asterisks for emphasis).",
        'kinesthetic': "Include hands-on activities, experiments, and interactive exercises. Provide real-world applications. Use PLAIN TEXT without markdown formatting (no asterisks for emphasis).",
        'unknown': "Balance visual, auditory, and kinesthetic learning approaches. Use PLAIN TEXT without markdown formatting (no asterisks for emphasis)."
    }
    
    style_guidance = style_prompts.get(learning_style, style_prompts['unknown'])
    
    prompt = f"""
    Create a comprehensive educational lesson on {topic} for grade {grade} students.
    {style_guidance}
    
    The lesson should include:
    1. An engaging introduction that explains what {topic} is and why it's important
    2. Main content with clear explanations of key concepts
    3. Examples and illustrations that make the topic relatable
    4. Historical context or background information
    5. Real-world applications of the topic
    6. Advanced concepts for deeper understanding
    7. Connections to related fields or subjects
    8. A brief summary of the main points
    9. 3-5 practice exercises or review questions
    
    DO NOT use markdown formatting such as asterisks (*) for emphasis. Use PLAIN TEXT only.
    Make the content educational, age-appropriate, and engaging.
    Organize the content into clear paragraphs with proper spacing between sections.
    """
    
    # Try with a moderate-sized response
    response = generate_content(prompt, language, max_tokens=1536)
    
    # Check if there was an error
    if isinstance(response, dict) and "error" in response:
        error_msg = response["error"]
        if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
            # If timeout, try again with a smaller maximum length
            logger.warning(f"Timeout generating lesson for {topic}. Retrying with smaller max_tokens.")
            response = generate_content(prompt, language, max_tokens=1024)
            
    # Convert the response to text
    result = extract_text_from_gemini_response(response)
    
    # Remove any asterisks that might have been used for markdown formatting
    result = re.sub(r'\*\*([^*]+)\*\*', r'\1', result)  # Remove bold asterisks
    result = re.sub(r'\*([^*]+)\*', r'\1', result)      # Remove italic asterisks
    
    # If the result is still an error, create a minimal lesson template
    if result.startswith('Error:'):
        logger.error(f"Failed to generate lesson for {topic}: {result}")
        return f"""Introduction to {topic}

This is a lesson about {topic} for grade {grade} students.

Key Concepts of {topic}

{topic} is an important subject to learn about. The main concepts include understanding its definition, history, and applications.

Historical Background of {topic}

{topic} has been studied for many years and has evolved over time.

Real-world Applications of {topic}

{topic} is used in many different ways in our everyday lives.

Examples of {topic}

Here are some examples that help explain {topic}.

Advanced Topics in {topic}

For students who want to learn more, here are some advanced ideas.

How {topic} Relates to Other Fields

{topic} connects to many other subjects you might be studying.

Case Studies in {topic}

Let's look at some specific examples or cases related to {topic}.

Current Research in {topic}

Scientists and researchers continue to explore new aspects of {topic}.

Practice and Review

Here are some questions to consider:
1. What is {topic}?
2. Why is {topic} important?
3. How can you apply what you've learned about {topic}?
4. What are the main concepts of {topic}?
5. How does {topic} connect to other subjects?
"""
    
    return result 