from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ScheduledAnalysis(db.Model):
    __tablename__ = 'scheduled_analyses'

    FREQ_ONCE = 'once'
    FREQ_DAILY = 'daily'
    FREQ_WEEKLY = 'weekly'
    FREQ_MONTHLY = 'monthly'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    platform = db.Column(db.String(20), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)
    source_input = db.Column(db.String(500), nullable=False)
    comment_limit = db.Column(db.Integer, default=100)
    frequency = db.Column(db.String(20), nullable=False, default=FREQ_ONCE)
    next_run_at = db.Column(db.DateTime, nullable=True)
    last_run_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    user = db.relationship('User', backref='scheduled_analyses', lazy='select')

    def __repr__(self):
        return f'<ScheduledAnalysis {self.id} ({self.frequency}) {self.source_input}>'
