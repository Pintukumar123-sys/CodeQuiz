from flask import Blueprint, render_template
from flask_login import login_required, current_user
from routes.quiz import LANGUAGES, LEVELS
import os
from werkzeug.utils import secure_filename
from flask import request, redirect, url_for, flash

main_bp = Blueprint('main', __name__)

def _best_language(scores):
    if not scores:
        return None

    from collections import Counter
    lang_counts = Counter(s['language'] for s in scores if 'language' in s)
    return lang_counts.most_common(1)[0][0] if lang_counts else None


@main_bp.route('/')
def home():
    from app import scores_col
    stats = {}
    if current_user.is_authenticated:
        user_scores = list(scores_col.find({'username': current_user.username}))
        stats = {
            'total_games': len(user_scores),
            'total_score': sum(s['score'] for s in user_scores),
            'avg_percentage': round(sum(s['percentage'] for s in user_scores) / len(user_scores)) if user_scores else 0,
            'best_language': _best_language(user_scores),
        }
    return render_template('main/home.html', languages=LANGUAGES, levels=LEVELS, stats=stats)

@main_bp.route('/profile')
@login_required
def profile():
    from app import scores_col
    scores = list(scores_col.find({'username': current_user.username}).sort('played_at', -1).limit(20))
    
    # Per-language breakdown
    breakdown = {}
    for lang in LANGUAGES:
        lang_scores = [s for s in scores if s['language'] == lang]
        if lang_scores:
            breakdown[lang] = {
                'games': len(lang_scores),
                'best': max(s['score'] for s in lang_scores),
                'avg_pct': round(sum(s['percentage'] for s in lang_scores) / len(lang_scores)),
            }

    return render_template('main/profile.html', scores=scores, breakdown=breakdown, languages=LANGUAGES, levels=LEVELS)

@main_bp.route('/profile/upload-photo', methods=['POST'])
@login_required
def upload_photo():
    from app import app
    if 'photo' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('main.profile'))
    
    file = request.files['photo']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('main.profile'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{current_user.id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Update user photo
        current_user.update_photo(filename)
        
        flash('Profile photo updated successfully!', 'success')
    else:
        flash('Invalid file type. Please upload a JPG, PNG, or GIF image.', 'error')
    
    return redirect(url_for('main.profile'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
