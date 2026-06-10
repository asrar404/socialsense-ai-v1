from datetime import datetime, timezone
from database import db

def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class EntityHistory(db.Model):
    __tablename__ = 'entity_history'

    id = db.Column(db.Integer, primary_key=True)
    normalized_name = db.Column(db.String(300), nullable=False, index=True)
    entity_type = db.Column(db.String(30), nullable=True)
    video_id = db.Column(db.String(20), nullable=True, index=True)
    channel_id = db.Column(db.String(200), nullable=True, index=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    sentiment_score = db.Column(db.Float, default=0.0)
    risk_score = db.Column(db.Float, default=0.0)
    mention_count = db.Column(db.Integer, default=0)
    importance_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    analysis = db.relationship('Analysis', backref=db.backref('entity_histories', lazy='dynamic', cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('entity_histories', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<EntityHistory {self.normalized_name} ({self.video_id})>'
