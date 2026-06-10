from datetime import datetime, timezone
from database import db

def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class ChannelContext(db.Model):
    __tablename__ = 'channel_contexts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    channel_id = db.Column(db.String(200), nullable=False, index=True)
    channel_name = db.Column(db.String(300), nullable=True)
    total_videos_analyzed = db.Column(db.Integer, default=0)
    total_entities_detected = db.Column(db.Integer, default=0)
    avg_sentiment = db.Column(db.Float, default=0.0)
    avg_risk = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    user = db.relationship('User', backref=db.backref('channel_contexts', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<ChannelContext {self.channel_name} ({self.channel_id})>'
