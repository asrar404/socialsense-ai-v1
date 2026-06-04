from datetime import datetime, timezone
from database import db


class RedditAnalysis(db.Model):
    __tablename__ = 'reddit_analyses'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False, unique=True, index=True)
    post_id = db.Column(db.String(20), nullable=False, index=True)
    subreddit = db.Column(db.String(100), nullable=True)
    post_title = db.Column(db.String(500), nullable=True)
    post_body = db.Column(db.Text, nullable=True)
    post_author = db.Column(db.String(200), nullable=True)
    post_score = db.Column(db.Integer, default=0)
    upvote_ratio = db.Column(db.Float, default=0.0)
    comment_count = db.Column(db.Integer, default=0)
    comment_limit = db.Column(db.Integer, default=100)
    permalink = db.Column(db.String(500), nullable=True)
    created_utc = db.Column(db.DateTime, nullable=True)
    is_demo = db.Column(db.Boolean, default=False)
    api_error = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f'<RedditAnalysis r/{self.subreddit} post/{self.post_id}>'
