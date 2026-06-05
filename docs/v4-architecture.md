# V4 Architecture — Advanced AI Analysis Engine

## Overview

V4 upgrades SocialSense AI from a simple rule-based analyzer into an AI-powered social media intelligence platform. Five new services replace the monolithic risk scoring with modular, explainable engines.

## Service Architecture

```
                     ┌─────────────────────────┐
                     │    analysis_service.py   │
                     │   (Orchestration Layer)  │
                     └────────────┬────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │         │          │          │          │
            ▼         ▼          ▼          ▼          ▼
   ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌──────────┐
   │Sentiment │ │ Toxicity │ │  Spam  │ │   Bot  │ │   Risk   │
   │ Service  │ │ Service  │ │ Service│ │Service │ │  Engine  │
   └──────────┘ └──────────┘ └────────┘ └────────┘ └──────────┘
```

### SentimentService

Lexicon-based sentiment analysis using positive/negative word lists with negation detection and intensifier weighting.

**Input:** `text: str`
**Output:** `{score, confidence, label, explanation}`

Labels: `Positive` (>=65), `Neutral` (36-64), `Negative` (<=35)

### ToxicityService

Multi-pattern toxicity detection scanning for:
- Profanity (13 patterns)
- Insults (5 patterns)
- Threats (6 patterns)
- Harassment (5 patterns)
- Hate language (2 patterns)
- Aggressive writing (4 patterns)

**Input:** `text: str`
**Output:** `{toxicity_score, confidence, toxicity_label, explanation}`

Labels: `Low` (<=15), `Medium` (<=40), `High` (<=70), `Critical` (>70)

### SpamService

Multi-factor spam detection:
- Promotional phrases (12 patterns)
- URL/link counting
- Excessive capitalization detection
- Emoji frequency (5+ threshold)
- Repeated character patterns
- Scam keyword matching
- Keyword stuffing detection
- Cross-comment duplicate detection (Jaccard similarity > 0.8)

**Input:** `text: str, all_texts: list`
**Output:** `{spam_score, confidence, spam_label, explanation}`

Labels: `Low` (<=15), `Medium` (<=40), `High` (<=70), `Critical` (>70)

### BotDetectionService

Bot/AI pattern detection using:
- Generic phrase matching (20 stock phrases)
- Template indicator patterns (8 structural regexes)
- Formality marker detection (3 sets of formal words)
- Vocabulary diversity analysis (unique word ratio)
- Sentence length uniformity
- Cross-comment Jaccard similarity > 0.6

⚠️ **Disclaimer:** "AI/Bot detection is probabilistic and should not be treated as proof."

### RiskEngine

Weighted combination of all factors:

| Factor | Weight |
|---|---|
| Toxicity | 35% |
| Spam | 25% |
| Bot score | 20% |
| Negative sentiment | 10% |
| Duplicate score | 10% |

**Output:** `{final_risk_score, final_risk_label, confidence, reasons[], recommendation}`

Labels: `Low` (<=15), `Medium` (<=40), `High` (<=70), `Critical` (>70)

## Database Changes

### Analysis table (new columns)
- `average_sentiment` (Float)
- `average_toxicity` (Float)
- `average_spam` (Float)
- `average_bot_score` (Float)
- `critical_comments_count` (Integer)
- `analysis_summary` (Text)

### CommentResult table (new columns)
- `spam_confidence` (Float)
- `toxicity_confidence` (Float)
- `sentiment_confidence` (Float)
- `bot_confidence` (Float)
- `recommendation` (Text)

## Analysis Summary

Auto-generated after every analysis:

```
Comments analyzed: 500
Positive: 42%
Neutral: 35%
Negative: 23%
Average Toxicity: 18%
High Risk Comments: 31
Overall Community Health: Moderate Risk
Key Concerns:
- Toxic language
- Promotional spam
- Duplicate posting
```

## Migration

```bash
flask db migrate -m "Version 4 AI engine upgrade"
flask db upgrade
```
