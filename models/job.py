from datetime import datetime, timezone
from database import db


class Job(db.Model):
    __tablename__ = 'jobs'

    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'
    TIMEOUT = 'TIMEOUT'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    platform = db.Column(db.String(50), nullable=False)
    source_type = db.Column(db.String(50), nullable=False)
    source_input = db.Column(db.String(500), nullable=False)
    comment_limit = db.Column(db.Integer, default=100)
    status = db.Column(db.String(20), nullable=False, default=PENDING, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    progress_percent = db.Column(db.Integer, default=0)
    current_step = db.Column(db.String(200), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    result_analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=True)
    cancellation_requested = db.Column(db.Boolean, default=False)
    execution_time_seconds = db.Column(db.Float, nullable=True)
    retry_count = db.Column(db.Integer, default=0)
    priority = db.Column(db.Integer, default=0)
    request_hash = db.Column(db.String(64), nullable=True, unique=True, index=True)

    user = db.relationship('User', backref='jobs', lazy='select')
    analysis = db.relationship('Analysis', backref='job', uselist=False)
    logs = db.relationship('JobLog', backref='job', lazy='dynamic', cascade='all, delete-orphan',
                           order_by='JobLog.timestamp')

    def __repr__(self):
        return f'<Job {self.id} ({self.status}) {self.platform}>'
