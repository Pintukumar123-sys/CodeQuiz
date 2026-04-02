from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime
import random

quiz_bp = Blueprint('quiz', __name__)

LANGUAGES = {
    'python': {'name': 'Python', 'icon': '🐍', 'color': '#3776AB'},
    'cpp': {'name': 'C++', 'icon': '⚡', 'color': '#00599C'},
    'java': {'name': 'Java', 'icon': '☕', 'color': '#ED8B00'},
    'javascript': {'name': 'JavaScript', 'icon': '🌐', 'color': '#F7DF1E'},
    'sql': {'name': 'SQL', 'icon': '🗄️', 'color': '#336791'},
    'dsa': {'name': 'DSA', 'icon': '🧠', 'color': '#9B59B6'},
}

LEVELS = {
    'easy': {'name': 'Easy', 'points': 10, 'time': 30},
    'medium': {'name': 'Medium', 'points': 20, 'time': 45},
    'hard': {'name': 'Hard', 'points': 30, 'time': 60},
}


@quiz_bp.route('/quiz')
@login_required
def quiz_home():
    return render_template('quiz/home.html', languages=LANGUAGES, levels=LEVELS)


@quiz_bp.route('/quiz/<language>/<level>')
@login_required
def start_quiz(language, level):
    if language not in LANGUAGES or level not in LEVELS:
        flash('Invalid quiz selection.', 'error')
        return redirect(url_for('quiz.quiz_home'))

    from app import questions_col
    # Load a random sample from the database so each quiz session gets a fresh set.
    total_questions = questions_col.count_documents({'language': language, 'level': level})
    if total_questions < 5:
        flash('Not enough questions available for this quiz. Please try another.', 'warning')
        return redirect(url_for('quiz.quiz_home'))

    sample_size = min(10, total_questions)
    selected = list(questions_col.aggregate([
        {'$match': {'language': language, 'level': level}},
        {'$sample': {'size': sample_size}},
    ]))

    # Shuffle the order of questions too
    random.shuffle(selected)

    # Store in session
    session['quiz'] = {
        'language': language,
        'level': level,
        'questions': [str(q['_id']) for q in selected],
        'current': 0,
        'score': 0,
        'answers': [],
        'shuffled_options': {},  # Added for tracking option shuffles
        'start_time': datetime.utcnow().isoformat(),
    }

    return redirect(url_for('quiz.question'))


@quiz_bp.route('/quiz/question', methods=['GET', 'POST'])
@login_required
def question():
    if 'quiz' not in session:
        return redirect(url_for('quiz.quiz_home'))

    quiz = session['quiz']
    current_idx = quiz['current']
    total = len(quiz['questions'])

    if current_idx >= total:
        return redirect(url_for('quiz.result'))

    from app import questions_col
    q = questions_col.find_one({'_id': ObjectId(quiz['questions'][current_idx])})
    if not q:
        return redirect(url_for('quiz.quiz_home'))
    
    # Shuffle options and track original correct answer
    if 'shuffled_options' not in quiz:
        quiz['shuffled_options'] = {}
    
    q_id_str = str(q['_id'])
    if q_id_str not in quiz['shuffled_options']:
        # Shuffle options for this question
        options = q['options'].copy()
        random.shuffle(options)
        quiz['shuffled_options'][q_id_str] = {
            'options': options,
            'correct_answer': q['correct_answer']
        }
        session['quiz'] = quiz
        session.modified = True
    
    # Use shuffled options for display
    shuffled = quiz['shuffled_options'][q_id_str]
    q['options'] = shuffled['options']
    q['correct_answer'] = shuffled['correct_answer']

    if request.method == 'POST':
        selected = request.form.get('answer')
        correct = q['correct_answer']
        is_correct = selected == correct
        points = LEVELS[quiz['level']]['points'] if is_correct else 0

        quiz['answers'].append({
            'question_id': str(q['_id']),
            'selected': selected,
            'correct': correct,
            'is_correct': is_correct,
        })
        quiz['score'] += points
        quiz['current'] += 1
        session['quiz'] = quiz
        session.modified = True

        if quiz['current'] >= total:
            return redirect(url_for('quiz.result'))

        return redirect(url_for('quiz.question'))

    level_info = LEVELS[quiz['level']]
    lang_info = LANGUAGES[quiz['language']]

    return render_template('quiz/question.html',
        question=q,
        current=current_idx + 1,
        total=total,
        level=level_info,
        language=lang_info,
        quiz=quiz,
    )


@quiz_bp.route('/quiz/result')
@login_required
def result():
    if 'quiz' not in session:
        return redirect(url_for('quiz.quiz_home'))

    quiz = session.pop('quiz')
    total = len(quiz['questions'])
    correct_count = sum(1 for a in quiz['answers'] if a['is_correct'])
    percentage = round((correct_count / total) * 100) if total else 0

    # Save score to DB
    from app import scores_col, questions_col
    score_doc = {
        'user_id': current_user.id,
        'username': current_user.username,
        'language': quiz['language'],
        'level': quiz['level'],
        'score': quiz['score'],
        'correct': correct_count,
        'total': total,
        'percentage': percentage,
        'answers': quiz['answers'],
        'played_at': datetime.utcnow(),
    }
    scores_col.insert_one(score_doc)

    lang_info = LANGUAGES[quiz['language']]
    level_info = LEVELS[quiz['level']]

    # Fetch full question details for review
    review = []
    for ans in quiz['answers']:
        q = questions_col.find_one({'_id': ObjectId(ans['question_id'])})
        if q:
            review.append({'question': q, 'answer': ans})

    return render_template('quiz/result.html',
        score=quiz['score'],
        correct=correct_count,
        total=total,
        percentage=percentage,
        language=lang_info,
        level=level_info,
        review=review,
    )
