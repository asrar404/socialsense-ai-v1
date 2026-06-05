from datetime import datetime, timezone
from database import db


class CommentResult(db.Model):
    __tablename__ = 'comment_results'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False, index=True)
    comment_text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(200), nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)

    spam_score = db.Column(db.Float, default=0.0)
    spam_explanation = db.Column(db.Text, nullable=True)
    spam_confidence = db.Column(db.Float, nullable=True)

    toxicity_score = db.Column(db.Float, default=0.0)
    toxicity_explanation = db.Column(db.Text, nullable=True)
    toxicity_confidence = db.Column(db.Float, nullable=True)

    sentiment = db.Column(db.String(20), nullable=True)
    sentiment_score = db.Column(db.Float, default=0.0)
    sentiment_explanation = db.Column(db.Text, nullable=True)
    sentiment_confidence = db.Column(db.Float, nullable=True)

    duplicate_score = db.Column(db.Float, default=0.0)
    duplicate_explanation = db.Column(db.Text, nullable=True)

    ai_like_score = db.Column(db.Float, default=0.0)
    ai_like_explanation = db.Column(db.Text, nullable=True)

    bot_score = db.Column(db.Float, default=0.0)
    bot_explanation = db.Column(db.Text, nullable=True)
    bot_confidence = db.Column(db.Float, nullable=True)

    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='Low')
    risk_explanation = db.Column(db.Text, nullable=True)
    recommendation = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f'<CommentResult {self.id} (Risk: {self.risk_level})>'
