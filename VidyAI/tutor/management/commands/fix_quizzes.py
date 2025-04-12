from django.core.management.base import BaseCommand
from tutor.models import Quiz, Question, Choice

class Command(BaseCommand):
    help = 'Fix quizzes with null passing_score values based on question count'

    def handle(self, *args, **options):
        # Get all quizzes
        quizzes = Quiz.objects.all()
        fixed_count = 0
        missing_questions_count = 0
        
        self.stdout.write(self.style.SUCCESS(f'Found {quizzes.count()} quizzes to check'))
        
        for quiz in quizzes:
            try:
                # Check if passing_score is None or 0
                needs_fix = quiz.passing_score is None or quiz.passing_score == 0
                
                # Count the number of questions
                question_count = quiz.questions.count()
                
                # Also fix quizzes that have questions but no passing score
                if needs_fix:
                    # Set passing score based on number of questions
                    if question_count <= 5:
                        passing_score = 80
                    elif question_count <= 10:
                        passing_score = 70
                    elif question_count <= 15:
                        passing_score = 65
                    else:
                        passing_score = 60
                    
                    # Update the quiz
                    quiz.passing_score = passing_score
                    quiz.save()
                    fixed_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'Fixed quiz "{quiz.title}" ({quiz.id}): {question_count} questions, {passing_score}% passing score'
                    ))
                
                # Check for quizzes with no questions but valid passing_score
                if question_count == 0:
                    self.stdout.write(self.style.WARNING(
                        f'Quiz "{quiz.title}" ({quiz.id}) has no questions but has passing_score={quiz.passing_score}%'
                    ))
                    missing_questions_count += 1
                    
                    # Default to creating placeholders if not specified and quiz has no questions
                    if options.get('add_placeholders') or options.get('auto_fix'):
                        # Create placeholder questions based on expected count
                        # Determine how many questions to create (default to 5)
                        num_placeholders = min(5, max(1, int(quiz.time_limit / 2)))
                        self.stdout.write(self.style.SUCCESS(
                            f'Creating {num_placeholders} placeholder questions for quiz "{quiz.title}" ({quiz.id})'
                        ))
                        
                        for i in range(num_placeholders):
                            # Create a placeholder question
                            question = Question.objects.create(
                                quiz=quiz,
                                question_text=f"Question {i+1}: This is a placeholder question. The original content was not available.",
                                question_type='multiple_choice',
                                explanation='Placeholder question created by fix_quizzes command'
                            )
                            
                            # Create placeholder choices
                            for j, choice_text in enumerate([f'Option A for Q{i+1}', f'Option B for Q{i+1}', 
                                                          f'Option C for Q{i+1}', f'Option D for Q{i+1}']):
                                Choice.objects.create(
                                    question=question,
                                    choice_text=choice_text,
                                    is_correct=(j == 0)  # Make the first option correct
                                )
                        
                        self.stdout.write(self.style.SUCCESS(
                            f'Created {num_placeholders} placeholder questions for quiz "{quiz.title}" ({quiz.id})'
                        ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error fixing quiz {quiz.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} quizzes'))
        if missing_questions_count > 0:
            self.stdout.write(self.style.WARNING(
                f'Found {missing_questions_count} quizzes with no questions. '
                f'Run with --add_placeholders to add placeholder questions.'
            ))
            
    def add_arguments(self, parser):
        parser.add_argument(
            '--add_placeholders',
            action='store_true',
            help='Add placeholder questions to quizzes with no questions',
        )
        parser.add_argument(
            '--auto_fix',
            action='store_true',
            help='Automatically fix all issues with quizzes',
        ) 