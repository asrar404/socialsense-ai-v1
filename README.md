# SocialSense AI

Multi-platform social media comment analysis engine. Analyzes YouTube and Reddit comments for spam, toxicity, sentiment, bot-like behavior, and overall risk.

## Features

- **Multi-Platform**: Analyze YouTube videos and Reddit posts
- **AI-Powered Analysis**: Sentiment, toxicity, spam, bot detection, and unified risk scoring
- **Explainable AI**: Every score includes confidence, label, and explanation
- **Analysis Summary**: Auto-generated summary with sentiment breakdown, toxicity average, and key concerns
- **Dashboard**: Platform-filtered stats, community health indicator, distribution charts
- **Exports**: CSV and JSON with full metadata, scores, confidence levels, and recommendations
- **Demo Mode**: Works without API keys using realistic simulated data

## Quick Start

```bash
cp .env.example .env
pip install -r requirements.txt
flask db upgrade
python app.py
```

## Requirements

- Python 3.14+
- Flask 3.1+
- SQLAlchemy 2.0+
- 8GB RAM (development)

## Configuration

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Flask secret key |
| `DATABASE_URL` | No | SQLite by default |
| `YOUTUBE_API_KEY` | No | Enables live YouTube data |
| `REDDIT_CLIENT_ID` | No | Enables live Reddit data |
| `REDDIT_CLIENT_SECRET` | No | Enables live Reddit data |
| `REDDIT_USER_AGENT` | No | Reddit API user agent |

## Architecture (V4)

```
services/
├── sentiment_service.py    # Lexicon-based sentiment analysis (0-100, 3 labels)
├── toxicity_service.py     # Pattern-based toxicity detection (4 severity levels)
├── spam_service.py         # Multi-factor spam detection (promo/links/caps/emojis)
├── bot_detection_service.py # Bot/AI pattern detection with disclaimer
├── risk_engine.py          # Unified weighted risk scoring with reasons/recommendation
├── analysis_service.py     # Orchestration layer (delegates to AI engines)
├── export_service.py       # CSV/JSON export with V4 fields
├── youtube_service.py      # YouTube Data API v3 integration
└── reddit_service.py       # Reddit API integration + demo data
```

### Score Meanings

| Score Range | Spam/Toxicity/Bot Label | Risk Label |
|---|---|---|
| 0-15 | Low | Low |
| 16-40 | Medium | Medium |
| 41-70 | High | High |
| 71-100 | Critical | Critical |

### Confidence Scale

| Range | Meaning |
|---|---|
| 0.0-0.3 | Low confidence |
| 0.3-0.6 | Medium confidence |
| 0.6-0.8 | High confidence |
| 0.8-1.0 | Very high confidence |

### Important Disclaimer

AI/Bot detection is probabilistic and should not be treated as proof. Scores are indicators, not definitive classifications. All bot detection results include this disclaimer automatically.

## Testing

```bash
python -m pytest -v
```

188 tests across:
- Sentiment Engine (8)
- Toxicity Engine (8)
- Spam Engine (10)
- Bot Detection Engine (9)
- Risk Engine (7)
- Dashboard Metrics (5)
- Analysis Summary (3)
- YouTube + Reddit routes/services
- CSV/JSON exports
- Auth flows
- Database models

## Version History

- **v4.0** — Advanced AI Analysis Engine (sentiment, toxicity, spam, bot engines, risk engine, summary generator)
- **v3.0** — Reddit integration (multi-platform)
- **v2.0** — YouTube API integration (pagination, enhanced dashboard)
- **v1.0** — Flask foundation (auth, demo mode, CSV export)

## Manual Verification

1. Start app: `python app.py`
2. Visit `http://localhost:5000`
3. Register account
4. Click "New Analysis" → YouTube tab → enter any video ID
5. Click "New Analysis" → Reddit tab → enter any post ID
6. Dashboard shows platform filter tabs
7. Analysis result page shows summary, charts, badges, explanations
8. Click CSV export → downloads with V4 fields
9. Click JSON export → includes analysis_summary and recommendations
