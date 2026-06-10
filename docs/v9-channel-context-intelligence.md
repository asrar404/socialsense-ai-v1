# V9 — Previous Video / Channel Context Intelligence

Upgrades the SocialSense AI analysis pipeline from:

```
Comment → Transcript Context → Entity Context
```

to:

```
Comment → Transcript Context → Entity Context → Previous Video Context → Channel Context → Historical Intelligence
```

---

## Architecture

```
User Input (URL)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                   AnalysisService                        │
│  ┌─────────────────────────────────────────────────┐    │
│  │ create_youtube_analysis / create_reddit_analysis │   │
│  └─────────────────────────────────────────────────┘    │
    │
    ├── 1. Fetch Metadata
    ├── 2. Fetch Comments
    ├── 3. V4 AI Analysis
    ├── 4. V7 Transcript Intelligence (YouTube)
    ├── 5. V8 Entity Intelligence
    └── 6. V9 Channel Context Intelligence
              │
              ├── ChannelContextService
              ├── VideoHistoryService
              ├── EntityHistoryService
              ├── TopicHistoryService
              ├── ContextIntelligenceService
              └── VideoComparisonService
```

### Data Flow

```
Entity Pipeline (V8)
    │
    ▼
┌─────────────────────┐
│ Channel Context     │  Create/update channel profile
│ Service             │  Tracks analyzed videos, entities
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Video History       │  Record video as historical entry
│ Service             │  Store avg_sentiment, avg_risk, entity_names
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Entity History      │  Track entity across channel videos
│ Service             │  sentiment_score, risk_score, frequency
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│ Context Intelligence│  Compute historical/entity/topic recurrence
│ Service             │  Generate trend_direction, aggregate scores
└─────────────────────┘
    │
    ▼
 DB: channel_contexts + video_context_history + entity_history
```

---

## Database Schema

### channel_contexts

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `user_id` | Integer (FK) | Owner |
| `channel_id` | String(200) | YouTube channel ID or subreddit name |
| `channel_name` | String(300) | Display name |
| `total_videos_analyzed` | Integer | Count |
| `total_entities_detected` | Integer | Count |
| `avg_sentiment` | Float | Channel-wide average sentiment |
| `avg_risk` | Float | Channel-wide average risk |
| `created_at` | DateTime | |
| `updated_at` | DateTime | |

### video_context_history

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `analysis_id` | Integer (FK) | Parent analysis |
| `user_id` | Integer (FK) | Owner |
| `video_id` | String(20) | YouTube video ID |
| `channel_id` | String(200) | Channel reference |
| `video_title` | String(500) | Title |
| `entity_count` | Integer | Entities in this video |
| `avg_sentiment` | Float | Average sentiment |
| `avg_risk` | Float | Average risk |
| `top_entities` | Text | JSON array of entity names |
| `processed_at` | DateTime | Timestamp |

### entity_history

| Column | Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `normalized_name` | String(300) | Entity canonical name (indexed) |
| `entity_type` | String(30) | PERSON, COMPANY, etc. |
| `video_id` | String(20) | YouTube video ID |
| `channel_id` | String(200) | Channel reference |
| `analysis_id` | Integer (FK, nullable) | Parent analysis |
| `user_id` | Integer (FK) | Owner |
| `sentiment_score` | Float | Entity sentiment in this video |
| `risk_score` | Float | Entity risk in this video |
| `mention_count` | Integer | Frequency |
| `importance_score` | Float | Importance in this video |
| `created_at` | DateTime | |

---

## Services

### ChannelContextService
- `get_or_create_channel(user_id, channel_id, channel_name)` — Get or create a channel profile
- `update_channel_stats(user_id, channel_id)` — Recalculate aggregate stats from all video histories
- `get_channel_intelligence(user_id, channel_id)` — Return channel metrics
- `get_all_channel_intelligence(user_id)` — Return all channel profiles for a user

### VideoHistoryService
- `record_video_analysis(analysis_id, user_id, video_id, channel_id, title, entity_count, avg_sentiment, avg_risk, top_entities)` — Record a completed video analysis in history
- `get_previous_videos(channel_id, user_id, exclude_analysis_id, limit)` — Retrieve past video analyses for a channel
- `find_recurring_entities(channel_id, user_id, exclude_analysis_id)` — Find entity names that reappear across channel videos
- `get_trend_statistics(channel_id, user_id, exclude_analysis_id, limit)` — Compute sentiment/risk/entity trends across history

### EntityHistoryService
- `record_entity_history(...)` — Record entity appearance across videos
- `get_entity_history(normalized_name, channel_id, user_id)` — Get entity's history across videos
- `get_entity_frequency(channel_id, user_id)` — Aggregate entity frequency for a channel
- `get_entity_sentiment_trend(normalized_name, channel_id, user_id)` — Sentiment trend over time
- `get_top_entities_by_channel(channel_id, user_id, limit)` — Most frequent entities per channel

### TopicHistoryService
- `get_recurring_topics(channel_id, user_id, limit)` — Extract topics that appear across videos
- `get_topic_trend(topic_name, channel_id, user_id, limit)` — Track a topic's appearances over time

### ContextIntelligenceService
- `compute_intelligence(user_id, channel_id, analysis_id, entity_names, current_sentiment, current_risk)` — Generate:
  - `historical_context` (0-100) — How much history does this channel have
  - `entity_recurrence` (0-100) — How many entities reappear
  - `topic_recurrence` (0-100) — Topic frequency score
  - `channel_relevance` (0-100) — Channel maturity score
  - `trend_score` (0-100) — Direction of sentiment/risk changes
  - `trend_direction` — positive / negative / stable

### VideoComparisonService
- `compare_with_channel_average(channel_id, user_id, current_sentiment, current_risk, current_entity_count)` — Compare current video to channel average
- `compare_with_top_video(channel_id, user_id, current_sentiment, current_risk, current_entity_count)` — Compare current video to best historical video

---

## Integration Points

### AnalysisService
- Both `create_youtube_analysis()` and `create_reddit_analysis()` run the V9 pipeline after V8 entity analysis:
  1. `ChannelContextService.get_or_create_channel()` — ensure channel exists
  2. `VideoHistoryService.record_video_analysis()` — save video to history
  3. `EntityHistoryService.record_entity_history()` — save each entity
  4. `ChannelContextService.update_channel_stats()` — refresh channel aggregates
  5. `ContextIntelligenceService.compute_intelligence()` — compute scores

### BackgroundWorker
- New progress stages: `Loading Channel History` (93%), `Computing Historical Trends` (95%), `Generating Context Intelligence` (97%)

### Dashboard
- New "Channel Intelligence" stat card showing `total_videos_analyzed`

### Result Page
- New "Channel Context Intelligence" card with:
  - Historical Context, Entity Recurrence, Topic Recurrence, Channel Relevance scores
  - Historical Trends (previous videos count, sentiment change, risk change)
  - Recurring Topics badges

### Exports
- CSV: `Historical Context Score`, `Historical Risk Score`, `Entity Recurrence Score`, `Topic Recurrence Score`, `Trend Direction` columns
- JSON: `video_context_history` and `entity_history` arrays

### Reports
- HTML reports include a Channel Intelligence section with total channels, videos, entities per channel

### Demo Mode
- `get_demo_channel_intelligence()`, `get_demo_context_intelligence()`, `get_demo_trend_statistics()`, `get_demo_video_history()`, `get_demo_entity_history()`, `get_demo_video_comparison()`

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `ENABLE_CHANNEL_INTELLIGENCE` | `true` | Master toggle for V9 channel context |
| `ENABLE_HISTORICAL_CONTEXT` | `true` | Enable recording of video history |
| `MAX_HISTORY_VIDEOS` | `100` | Max videos tracked per channel |
| `MAX_ENTITY_HISTORY` | `500` | Max entity history records |

---

## Testing

```bash
python -m pytest tests/test_v9.py -v     # 39 V9 tests
```

Coverage:
- ChannelContext model (4)
- VideoContextHistory model (4)
- EntityHistory model (5)
- ChannelContextService (4)
- VideoHistoryService (5)
- EntityHistoryService (4)
- TopicHistoryService (1)
- ContextIntelligenceService (3)
- VideoComparisonService (2)
- Dashboard integration (1)
- Demo mode (6)

All V1-V8 tests continue passing. 90 total V8+V9 tests pass.

---

## Known Limitations

1. **Per-channel, not cross-channel** — Intelligence is computed per YouTube channel or Reddit subreddit, not across all channels.
2. **No relationship graphs** — Entities are tracked individually; no relationship detection between entities across videos.
3. **Topic tracking is transcript-dependent** — Only works for YouTube analyses with available transcripts.
4. **Aggregate only** — Trend analysis uses simple first-half/second-half comparison; no time-series decomposition.
5. **No alerting** — Intelligence scores are displayed but don't trigger notifications.

---

## V10 Roadmap

1. Multimodal Intelligence (audio/visual analysis)
2. Entity relationship graphs across videos
3. Time-series trend analytics
4. Cross-channel intelligence
5. Transformer model integration
6. Historical alerting (notify when entity risk spikes across videos)
7. Graph exports

---

## Version History

- **v9.0** — Previous Video / Channel Context Intelligence
- **v8.0** — Person/Entity Context Intelligence
- **v7.0** — Transcript-Aware Comment Intelligence
- **v6.0** — Monitoring, Scheduling, Notifications, Reports
- **v5.0** — Background Jobs
- **v4.0** — Advanced AI Analysis Engine
- **v3.0** — Reddit Integration
- **v2.0** — YouTube API Integration
- **v1.0** — Flask Foundation
