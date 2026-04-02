# CodeQuiz
CodeQuiz is a modern, full-stack programming quiz web app built with Flask + MongoDB and designed for students & learners who want a clean, interactive way to master coding topics.It supports user auth, session-based quizzes, leaderboard competition, and personal performance tracking.

What it does :-

User registration + login + secure session management.
6 language tracks: Python, C++, Java, JavaScript, SQL, DSA.
3 levels: Easy, Medium, Hard.
Timed 10-question rounds, point-based scoring.
Stores each quiz result in MongoDB and builds per-user statistics.
Leaderboard with filtering by language and level.
Quiz review with answer explanations.
Auto-seeding of question bank on first run.
Profile page with history and per-language analytics.
File upload support (user avatar, 2MB max).

Tech stack:-

Backend: Flask, Flask-Login, PyMongo
DB: MongoDB (local or Atlas)
Templates: Jinja2
Production-ready runner: Gunicorn
Config: .env, SECRET_KEY, MONGO_URI

Why it’s useful :-

Instant coding self-assessment tool with structured points and progression.
Good demo for full-stack dev skills: auth, DB, session, UI, API design.
Extensible: add languages, quiz modes, multiplayer, or AI question generation
