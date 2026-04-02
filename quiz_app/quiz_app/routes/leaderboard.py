from flask import Blueprint, render_template
from flask_login import login_required, current_user
from routes.quiz import LANGUAGES, LEVELS

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard')
@leaderboard_bp.route('/leaderboard/<language>')
@leaderboard_bp.route('/leaderboard/<language>/<level>')
def leaderboard(language=None, level=None):
    from app import scores_col

    match = {}
    if language and language in LANGUAGES:
        match['language'] = language
    if level and level in LEVELS:
        match['level'] = level

    pipeline = [
        {'$match': match},
        {'$group': {
            '_id': '$username',
            'total_score': {'$sum': '$score'},
            'games_played': {'$sum': 1},
            'avg_percentage': {'$avg': '$percentage'},
            'best_score': {'$max': '$score'},
        }},
        {'$sort': {'total_score': -1}},
        {'$limit': 50},
    ]

    entries = list(scores_col.aggregate(pipeline))

    # Recent activity
    recent = list(scores_col.find(match).sort('played_at', -1).limit(10))

    return render_template('leaderboard/index.html',
        entries=entries,
        recent=recent,
        languages=LANGUAGES,
        levels=LEVELS,
        active_language=language,
        active_level=level,
    )
