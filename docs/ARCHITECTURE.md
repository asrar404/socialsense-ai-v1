# SocialSense AI - Architecture Overview

## Architecture Pattern

Clean Architecture with Service Layer and Repository Pattern.

## Layer Structure

### 1. Presentation Layer (routes/)
- Flask Blueprints handling HTTP requests/responses
- Template rendering with Jinja2
- Form validation
- Session management via Flask-Login

### 2. Service Layer (services/)
- Business logic encapsulation
- Orchestration between controllers and repositories
- Risk scoring, analysis, and export logic
- Demo mode handling

### 3. Repository Layer (repositories/)
- Data access abstraction
- CRUD operations
- Complex query methods
- Decouples business logic from ORM

### 4. Model Layer (models/)
- SQLAlchemy ORM models
- Database schema definition
- Relationships and constraints

### 5. Configuration Layer (config/)
- Environment-based configuration
- Development/Production/Testing presets

## Data Flow

```
User Request
    -> Route Handler (Blueprint)
        -> Service Layer (Business Logic)
            -> Repository Layer (Data Access)
                -> Model Layer (Database)
            <- Domain Objects
        <- Processed Results
    -> Template Rendering
<- HTML Response
```

## Key Design Decisions

### Why Service Layer?
- Keeps routes thin
- Centralizes business logic
- Testable independently
- Reusable across routes

### Why Repository Pattern?
- Abstracts database access
- Makes testing easier (mocking)
- Consistent query interface
- Future DB migration friendly

### Why Demo Mode?
- Allows evaluation without API keys
- Full feature demonstration
- Clear visual indicators
- Easy transition to live mode

## Security Architecture

- CSRF protection via Flask-WTF
- Password hashing with Werkzeug
- HTTP-only session cookies
- Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection)
- Input validation at service layer
- ORM-based SQL injection protection
- Environment variables for secrets

## Database Design

### Users
- id (PK)
- username (unique, indexed)
- email (unique, indexed)
- password_hash
- created_at, updated_at

### Analyses
- id (PK)
- user_id (FK -> users)
- analysis_type
- created_at, updated_at

### YouTubeAnalyses
- id (PK)
- analysis_id (FK -> analyses, unique)
- video_id (indexed)
- video_title, channel_name
- comment_count, is_demo

### CommentResults
- id (PK)
- analysis_id (FK -> analyses, indexed)
- comment_text, author
- spam_score, toxicity_score
- sentiment, sentiment_score
- duplicate_score, ai_like_score, bot_score
- risk_score, risk_level
- Explanations for all scores

### ReportExports
- id (PK)
- analysis_id (FK -> analyses)
- format_type, file_path
- created_at

## Risk Scoring Algorithm

```python
risk = (
    spam * 0.20 +
    toxicity * 0.25 +
    normalized_sentiment * 0.10 +
    duplicate * 0.10 +
    ai_like * 0.15 +
    bot * 0.20
)
```

### Risk Levels
- 0-25: Low
- 26-50: Medium
- 51-75: High
- 76-100: Critical
