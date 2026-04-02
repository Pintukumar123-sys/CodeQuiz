# 🧠 CodeQuiz — Programming Quiz Web App

A full-stack quiz platform built with **Flask**, **MongoDB**, and **Flask-Login**.

## Features

- 🔐 **Auth** — Register, Login, Logout with session management
- 🌐 **6 Quiz Topics** — Python, C++, Java, JavaScript, SQL, DSA
- 🎯 **3 Difficulty Levels** — Easy (10pts), Medium (20pts), Hard (30pts)
- ⏱️ **Live Timer** — Per-question countdown with visual warning
- 📊 **Leaderboard** — Filterable by language and level
- 👤 **Profile Page** — Personal stats, history, per-language breakdown
- 💡 **Answer Review** — Explanations after each quiz
- 🌱 **Auto Seed** — 70+ questions seeded on first run

## Project Structure

```
quiz_app/
├── app.py               # Flask app factory, DB connection, blueprints
├── requirements.txt
├── .env.example
├── models/
│   └── user.py          # User model (Flask-Login compatible)
├── routes/
│   ├── auth.py          # /login  /register  /logout
│   ├── quiz.py          # /quiz  /quiz/<lang>/<level>  /quiz/question  /quiz/result
│   ├── leaderboard.py   # /leaderboard  /leaderboard/<lang>/<level>
│   └── main.py          # /  /profile
├── data/
│   └── seed.py          # Seeds 70+ questions into MongoDB
└── templates/
    ├── base.html
    ├── auth/            login.html  register.html
    ├── quiz/            home.html  question.html  result.html
    ├── leaderboard/     index.html
    └── main/            home.html  profile.html
```

## Setup & Run

### 1. Prerequisites

- Python 3.9+
- MongoDB running locally (`mongod`) **OR** a MongoDB Atlas URI

### 2. Install dependencies

```bash
cd quiz_app
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY and MONGO_URI
```

### 4. Run the app

```bash
python app.py
```

The app will:
- Connect to MongoDB
- Auto-seed 70+ questions (only on first run)
- Start on http://127.0.0.1:5000

### 5. Open in browser

```
http://localhost:5000
```

Register an account and start quizzing!

---

## MongoDB Collections

| Collection  | Purpose                          |
|-------------|----------------------------------|
| `users`     | User accounts (hashed passwords) |
| `scores`    | Every quiz attempt with answers  |
| `questions` | Question bank (seeded on start)  |

## Adding More Questions

Edit `data/seed.py` and add dicts in this format:

```python
{
    'language': 'python',     # python / cpp / java / javascript / sql / dsa
    'level': 'medium',        # easy / medium / hard
    'question': 'What does ... do?',
    'options': ['A', 'B', 'C', 'D'],
    'correct_answer': 'B',
    'explanation': 'Because ...'
}
```

Then delete the `questions` collection in MongoDB and restart — it will re-seed.

## Tech Stack

| Layer     | Tech                        |
|-----------|-----------------------------|
| Backend   | Python, Flask               |
| Auth      | Flask-Login, Werkzeug       |
| Database  | MongoDB, PyMongo            |
| Frontend  | Jinja2, CSS3, Vanilla JS    |
| Fonts     | Syne + Space Mono (Google)  |
