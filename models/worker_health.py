from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class WorkerHealth(db.Model):
    __tablename__ = 'worker_health'

    ONLINE = 'online'
    OFFLINE = 'offline'
    DEGRADED = 'degraded'

    id = db.Column(db.Integer, primary_key=True)
    worker_name = db.Column(db.String(100), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default=ONLINE)
    last_heartbeat_at = db.Column(db.DateTime, nullable=True)
    active_jobs = db.Column(db.Integer, default=0)
    queue_length = db.Column(db.Integer, default=0)
    processed_jobs_count = db.Column(db.Integer, default=0)
    failed_jobs_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    def __repr__(self):
        return f'<WorkerHealth {self.worker_name} ({self.status})>'
