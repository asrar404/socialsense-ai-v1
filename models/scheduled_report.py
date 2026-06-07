from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ScheduledReport(db.Model):
    __tablename__ = 'scheduled_reports'

    FREQ_DAILY = 'daily'
    FREQ_WEEKLY = 'weekly'
    FREQ_MONTHLY = 'monthly'

    FORMAT_HTML = 'html'
    FORMAT_CSV = 'csv'
    FORMAT_JSON = 'json'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    report_type = db.Column(db.String(20), nullable=False, default=FREQ_DAILY)
    frequency = db.Column(db.String(20), nullable=False, default=FREQ_DAILY)
    platform_filter = db.Column(db.String(20), nullable=True)
    report_format = db.Column(db.String(10), nullable=False, default=FORMAT_HTML)
    next_run_at = db.Column(db.DateTime, nullable=True)
    last_run_at = db.Column(db.DateTime, nullable=True)
    last_file_path = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    user = db.relationship('User', backref='scheduled_reports', lazy='select')

    def __repr__(self):
        return f'<ScheduledReport {self.id} ({self.frequency})>'
