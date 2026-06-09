# V8 — Person/Entity Context Intelligence

Upgrades the SocialSense AI analysis pipeline from:

```
Comment → Transcript → Context Relevance
```

to:

```
Comment → Transcript → Entity Detection → Entity Sentiment → Entity Risk → Entity Summary
```

---

## Architecture

```
User Input (URL)
    │
    ▼
┌─────────────────────────────────────────────────┐
│               AnalysisService                    │
│  ┌───────────────────────────────────────────┐  │
│  │ create_youtube_analysis /                 │  │
│  │ create_reddit_analysis                    │  │
│  └───────────────────────────────────────────┘  │
    │
    ├── 1. Fetch Metadata (video/post info)
    ├── 2. Fetch Comments
    ├── 3. V4 AI Analysis (sentiment, toxicity, spam, bot, risk)
    ├── 4. V7 Transcript Intelligence (if YouTube)
    └── 5. V8 Entity Intelligence
              │
              ├── EntityExtractionService
              ├── EntityResolutionService
              ├── EntityIntelligenceService
              ├── EntitySentimentService
              ├── EntityRiskService
              └── EntitySummaryService
```

### Data Flow

```
Raw Text (title, description, transcript, comments)
    │
    ▼
┌─────────────────────┐
│ Entity Extraction   │  Regex patterns + spaCy (optional)
│ Service             │  Returns: [name, type, source, frequency]
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Entity Resolution   │  Normalizes aliases (openai → OpenAI, msft → Microsoft)
│ Service             │  Deduplicates across sources
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Entity Intelligence │  Computes importance_score, relevance_score, relationship
│ Service             │  Sorts by importance
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Entity Sentiment    │  Per-comment, per-entity sentiment
│ Service             │  Window-based, negation-aware
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Entity Risk         │  Targeting, harassment, misinformation, spam, coordinated
│ Service             │  Per-entity risk aggregation
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Entity Summary      │  Most discussed person/company/product
│ Service             │  Most controversial/positive/negative entity
└─────────────────────┘
    │
    ▼
 DB: entities + entity_mentions + entity_contexts
```

---

## Database Schema

### entities

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `analysis_id` | Integer (FK) | Parent analysis |
| `name` | String(300) | Raw extracted name |
| `normalized_name` | String(300) | Canonical form after resolution |
| `entity_type` | String(30) | PERSON, COMPANY, BRAND, PRODUCT, ORGANIZATION, LOCATION, EVENT, TOPIC, OTHER |
| `source` | String(20) | title, description, transcript, comment, combined |
| `frequency` | Integer | Total occurrence count |
| `importance_score` | Float | 0-100, relative to most frequent entity |
| `created_at` | DateTime | |
| `updated_at` | DateTime | |

### entity_mentions

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `entity_id` | Integer (FK) | Parent entity |
| `comment_result_id` | Integer (FK, nullable) | Comment where mentioned |
| `transcript_segment_id` | Integer (FK, nullable) | Transcript segment where mentioned |
| `mention_text` | String(300) | Text as it appeared |
| `mention_source` | String(20) | title, description, transcript, comment |
| `context_snippet` | Text | Surrounding text |
| `created_at` | DateTime | |

### entity_contexts

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `entity_id` | Integer (FK) | Parent entity |
| `comment_result_id` | Integer (FK) | Related comment |
| `entity_sentiment` | String(20) | positive, negative, neutral |
| `entity_sentiment_score` | Float | 0-100 |
| `entity_risk_score` | Float | 0-100 |
| `entity_relevance_score` | Float | 0-100 |
| `entity_context_label` | String(30) | highly_related, related, partially_related, unrelated, unknown |
| `reason` | Text | Explainable reason |
| `created_at` | DateTime | |

---

## Entity Extraction

### Pattern-Based (Default)

The `EntityExtractionService` uses compiled regex patterns:

**People** — Capitalized two-word names (`Elon Musk`), honorifics (`Dr. Smith`)

**Companies** — Suffix patterns (`MicrosoftCorp`, `Tesla Inc`), keyword matching (`Technologies`, `Systems`)

**Products** — Known names (`iPhone`, `ChatGPT`, `Model 3 Pro`), versioned patterns

### spaCy Integration (Optional)

```bash
pip install spacy
python -m spacy download en_core_web_sm
```

NER labels mapped:

| spaCy Label | Entity Type |
|---|---|
| `PERSON` | PERSON |
| `ORG` | ORGANIZATION |
| `GPE` | LOCATION |
| `PRODUCT` | PRODUCT |
| `EVENT` | EVENT |

Extraction runs across all four text sources independently, then merges by normalized name.

---

## Entity Resolution

The `EntityResolutionService` normalizes names:

| Raw | Canonical |
|---|---|
| `openai`, `Open AI`, `OPENAI` | `OpenAI` |
| `msft`, `Microsoft` | `Microsoft` |
| `tsla`, `Tesla` | `Tesla` |
| `chatgpt`, `gpt4`, `gpt-4` | `ChatGPT` |

Custom aliases at runtime: `resolution_service.add_alias('myco', 'MyCompany')`

---

## Entity Sentiment

Window-based per-entity sentiment:

1. Find mentions by regex
2. Extract 40-char window around each mention
3. Score with positive/negative keywords, intensifiers (x1.5), and negation (flip)

| Comment | Entity | Sentiment | Score |
|---|---|---|---|
| `Tesla is amazing and great!` | Tesla | positive | 80.0 |
| `Tesla is terrible` | Tesla | negative | 20.0 |
| `Tesla is not bad` | Tesla | positive | 65.0 |
| `I like Apple` | Tesla | neutral | 50.0 |

---

## Entity Risk

| Factor | Score | Trigger |
|---|---|---|
| Targeted attack | +35 | `hate you`, `kill him` |
| Harassment keywords | +10 | `idiot`, `fraud`, `liar` |
| Misinformation | +20 | `fake news`, `propaganda` |
| Spam promotional | +15 | `buy now`, `click here` |
| Coordinated | +25 | `join this`, `upvote this` |
| Negative sentiment | +5 | Overall negative comment |

Capped at 100. Includes explainable reasons.

---

## Dashboard Integration

- **Entities stat card** — Total entities across all analyses
- **Entity Risk** in Community Health card
- **Entity Type Distribution** doughnut chart
- **Entity Risk Distribution** bar chart

---

## Result Page Integration

- **Summary cards**: Most Discussed Person, Company, Controversial Entity
- **Entity table**: Name, Type badge, Frequency, Importance bar, Source

---

## Export Format

CSV columns added: `Entities, Entity Types, Entity Sentiments, Entity Risk Scores, Entity Relevance Scores`

JSON includes `entity_summary` object and per-comment `entity_mentions`, `entity_sentiments`, `entity_risks`.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `ENABLE_ENTITY_ANALYSIS` | `true` | Master toggle |
| `ENABLE_ENTITY_SENTIMENT` | `true` | Per-entity sentiment |
| `ENABLE_ENTITY_RISK` | `true` | Per-entity risk |
| `MAX_ENTITIES_PER_ANALYSIS` | `100` | Max entities stored |
| `ENTITY_MIN_IMPORTANCE` | `5` | Min importance threshold |

---

## Testing

```bash
python -m pytest tests/test_v8.py -v     # 51 V8 tests
python -m pytest                          # 454+ total
```

---

## Known Limitations

1. Regex extraction < transformer NER
2. Keyword sentiment misses sarcasm
3. Risk heuristics need per-community tuning
4. No cross-analysis entity tracking (V9)
5. No relationship graph (V9)

---

## Transformer Upgrade Path

Services are designed for drop-in transformer replacement:

```python
# Current
class EntityExtractionService:
    def extract_from_texts(self, title='', ...):
        # regex

# Future
class EntityExtractionService:
    def __init__(self):
        self.model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
    def extract_from_texts(self, title='', ...):
        # NER
```

| Service | Current | Future |
|---|---|---|
| Extraction | Regex + spaCy | `dslim/bert-base-NER` |
| Resolution | Dictionary | Embedding similarity |
| Sentiment | Keywords | `cardiffnlp/twitter-roberta-base-sentiment` |
| Risk | Heuristics | Fine-tuned classifier |

---

## V9 Roadmap

1. Cross-analysis entity tracking
2. Entity relationship graphs
3. Temporal entity trends
4. Multimodal entities
5. Transformer model integration
6. Entity alerting
7. Graph exports

---

## Version History

- **v8.0** — Person/Entity Context Intelligence
- **v7.0** — Transcript-Aware Comment Intelligence
- **v6.0** — Monitoring, Scheduling, Notifications, Reports
- **v5.0** — Background Jobs
- **v4.0** — Advanced AI Analysis Engine
- **v3.0** — Reddit Integration
- **v2.0** — YouTube API Integration
- **v1.0** — Flask Foundation
