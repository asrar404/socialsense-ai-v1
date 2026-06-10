from datetime import datetime, timezone
from database import db

def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class VideoContextHistory(db.Model):
    __tablename__ = 'video_context_history'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    video_id = db.Column(db.String(20), nullable=False, index=True)
    channel_id = db.Column(db.String(200), nullable=True, index=True)
    video_title = db.Column(db.String(500), nullable=True)
    entity_count = db.Column(db.Integer, default=0)
    avg_sentiment = db.Column(db.Float, default=0.0)
    avg_risk = db.Column(db.Float, default=0.0)
    top_entities = db.Column(db.Text, nullable=True)
    processed_at = db.Column(db.DateTime, default=_now, nullable=False)

    analysis = db.relationship('Analysis', backref=db.backref('video_context_history', uselist=False, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('video_context_histories', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<VideoContextHistory {self.video_id} ({self.channel_id})>'
