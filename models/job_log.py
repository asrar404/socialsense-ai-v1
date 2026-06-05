from datetime import datetime, timezone
from database import db


class JobLog(db.Model):
    __tablename__ = 'job_logs'

    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    level = db.Column(db.String(20), nullable=False, default=INFO)
    step = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    metadata_json = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<JobLog {self.id} ({self.level}) job:{self.job_id}>'
