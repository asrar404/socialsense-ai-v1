from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Notification(db.Model):
    __tablename__ = 'notifications'

    TYPE_JOB_COMPLETED = 'job_completed'
    TYPE_JOB_FAILED = 'job_failed'
    TYPE_JOB_CANCELLED = 'job_cancelled'
    TYPE_SCHEDULE_CREATED = 'scheduled_analysis_created'
    TYPE_SCHEDULE_FAILED = 'scheduled_analysis_failed'
    TYPE_REPORT_GENERATED = 'report_generated'
    TYPE_HIGH_RISK = 'high_risk_detected'
    TYPE_SYSTEM_WARNING = 'system_warning'

    SEVERITY_INFO = 'info'
    SEVERITY_SUCCESS = 'success'
    SEVERITY_WARNING = 'warning'
    SEVERITY_DANGER = 'danger'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), nullable=False, default=SEVERITY_INFO)
    is_read = db.Column(db.Boolean, default=False)
    link_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    user = db.relationship('User', backref='notifications', lazy='select')

    def __repr__(self):
        return f'<Notification {self.id} ({self.type})>'
