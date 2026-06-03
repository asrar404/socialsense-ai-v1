# SocialSense AI

AI-powered YouTube comment intelligence platform that analyzes comments for spam, toxicity, sentiment, AI-generated content, and bot behavior.

## Features

- **YouTube Comment Analysis** - Extract and analyze comments from any public YouTube video
- **Spam Detection** - Identify promotional content, link dropping, and engagement bait
- **Toxicity Detection** - Flag aggressive or offensive language
- **Sentiment Analysis** - Classify comments as Positive, Neutral, or Negative
- **AI-like Writing Detection** - Identify possible AI-generated comments
- **Bot Behavior Detection** - Spot bot-like patterns
- **Risk Scoring** - Multi-factor risk assessment (0-100)
- **Demo Mode** - Full functionality without YouTube API key
- **CSV Export** - Download detailed reports
- **Analytics Dashboard** - Visual charts and statistics
- **Dark Mode** - Modern, eye-friendly UI

## Technology Stack

- **Backend**: Python 3.12+, Flask, SQLAlchemy
- **Database**: SQLite (SQLAlchemy ORM)
- **Frontend**: Bootstrap 5, Chart.js, Font Awesome
- **Analysis**: Custom NLP scoring engine
- **Testing**: pytest

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd socialsense-ai
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK data (first run)

```bash
python -m nltk.downloader punkt
```

### 5. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///socialsense.db
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 6. Run the application

```bash
python app.py
```

Or with Flask CLI:

```bash
flask run
```

The application will be available at `http://127.0.0.1:5000`

### 7. Run tests

```bash
pytest
```

For coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

## Demo Mode

If `YOUTUBE_API_KEY` is not set in `.env`, the application automatically runs in **Demo Mode** with simulated data. A yellow banner is displayed:

> **Demo Mode Active** - YouTube API key not configured. Using simulated data for demonstrations.

All features work identically in Demo Mode.

## Project Structure

```
socialsense-ai/
├── app.py                    # Application factory
├── config/
│   ├── __init__.py
│   └── settings.py           # Configuration classes
├── models/
│   ├── user.py               # User model
│   ├── analysis.py           # Analysis & YouTubeAnalysis models
│   ├── comment_result.py     # CommentResult model
│   └── report_export.py      # ReportExport model
├── repositories/
│   ├── base.py               # Base repository
│   ├── user_repository.py
│   ├── analysis_repository.py
│   ├── comment_result_repository.py
│   └── report_export_repository.py
├── services/
│   ├── auth_service.py       # Authentication logic
│   ├── youtube_service.py    # YouTube API integration
│   ├── analysis_service.py   # Analysis orchestration
│   ├── risk_scoring_service.py  # Scoring algorithms
│   ├── export_service.py     # CSV export
│   └── demo_service.py       # Demo data provider
├── routes/
│   ├── auth_routes.py        # Login/register/logout/profile
│   ├── dashboard_routes.py   # Analytics dashboard
│   ├── analysis_routes.py    # New/result/history
│   └── export_routes.py      # CSV download
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   ├── dashboard/
│   ├── analysis/
│   └── errors/
├── static/
│   ├── css/style.css
│   └── js/main.js
├── tests/
│   ├── test_auth.py
│   ├── test_models.py
│   ├── test_routes.py
│   ├── test_analysis.py
│   ├── test_risk_scoring.py
│   ├── test_demo.py
│   ├── test_csv_export.py
│   └── test_services.py
├── docs/
│   ├── ARCHITECTURE.md
│   └── VERSION_1_SCOPE.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Known Limitations

- English-optimized analysis
- Comment volume limited to ~50 per analysis in live mode
- NLP is rule-based (not ML-model based)
- SQLite suitable for single-user/small-scale only

## License

MIT
