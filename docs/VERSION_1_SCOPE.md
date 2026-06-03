# SocialSense AI - Version 1 Scope

## In Scope (Version 1 - MVP)

### Core Features
- [x] User registration and authentication
- [x] YouTube video comment analysis
- [x] Spam detection
- [x] Toxicity detection
- [x] Sentiment analysis (Positive/Neutral/Negative)
- [x] Duplicate content detection
- [x] AI-like writing indicators
- [x] Bot-like behavior indicators
- [x] Overall risk scoring
- [x] Demo mode (no API key required)
- [x] CSV export
- [x] Analytics dashboard
- [x] Analysis history
- [x] Dark mode UI
- [x] Responsive design
- [x] Comprehensive test suite

### Architecture
- [x] Service Layer pattern
- [x] Repository pattern
- [x] Flask Blueprints
- [x] SQLite database (SQLAlchemy ORM)
- [x] Environment-based configuration

### Analysis Engine
- [x] Multi-factor risk scoring
- [x] Human-readable explanations
- [x] Probabilistic disclaimers
- [x] No false certainty claims

## Out of Scope (Version 2+)

### Not Implemented
- Reddit analysis
- Transcript analysis
- Video content analysis
- Audio analysis
- Admin system
- Docker deployment
- PostgreSQL production infrastructure
- Advanced multimodal AI features
- OAuth/social login
- Email verification
- Password reset
- Real-time analysis
- Batch analysis
- API rate limiting
- Caching layer
- Webhook notifications
- Team/collaboration features

## Known Limitations (Version 1)

1. **Demo Mode**: Uses curated sample data, not real YouTube comments
2. **YouTube API**: Requires API key for live data; subject to quota limits
3. **Analysis Depth**: NLP analysis is rule-based, not ML-model based
4. **Scalability**: SQLite suitable for single-user/small-scale only
5. **Performance**: No caching; repeated analyses hit database each time
6. **Language Support**: English-optimized analysis
7. **Comment Volume**: Limited to ~50 comments per analysis in live mode

## Version 2 Roadmap (Planned)

1. PostgreSQL support
2. Reddit integration
3. Enhanced ML-based NLP models
4. Admin dashboard
5. Email notifications
6. API rate limiting
7. Batch analysis
8. Export to PDF
9. OAuth authentication
10. Docker deployment
