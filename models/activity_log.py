from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    ACTION_ANALYSIS_SUBMITTED = 'analysis_submitted'
    ACTION_JOB_STARTED = 'job_started'
    ACTION_JOB_COMPLETED = 'job_completed'
    ACTION_JOB_FAILED = 'job_failed'
    ACTION_JOB_CANCELLED = 'job_cancelled'
    ACTION_EXPORT_DOWNLOADED = 'export_downloaded'
    ACTION_SCHEDULE_CREATED = 'schedule_created'
    ACTION_SCHEDULE_PAUSED = 'schedule_paused'
    ACTION_NOTIFICATION_READ = 'notification_read'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(500), nullable=True)
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    user = db.relationship('User', backref='activity_logs', lazy='select')

    def __repr__(self):
        return f'<ActivityLog {self.id} ({self.action})>'
