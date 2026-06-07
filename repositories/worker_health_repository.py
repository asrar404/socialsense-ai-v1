from models.worker_health import WorkerHealth
from repositories.base import BaseRepository
from database import db
from datetime import datetime, timezone


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class WorkerHealthRepository(BaseRepository):
    def __init__(self):
        super().__init__(WorkerHealth)

    def get_or_create(self, worker_name):
        health = self.model.query.filter_by(worker_name=worker_name).first()
        if not health:
            health = WorkerHealth(worker_name=worker_name)
            db.session.add(health)
            db.session.commit()
        return health

    def record_heartbeat(self, worker_name, active_jobs=0, queue_length=0):
        health = self.get_or_create(worker_name)
        health.last_heartbeat_at = _now()
        health.status = WorkerHealth.ONLINE
        health.active_jobs = active_jobs
        health.queue_length = queue_length
        db.session.commit()
        return health

    def mark_offline(self, worker_name):
        health = self.get_or_create(worker_name)
        health.status = WorkerHealth.OFFLINE
        db.session.commit()
        return health

    def get_online_workers(self):
        return self.model.query.filter_by(status=WorkerHealth.ONLINE).all()

    def get_summary(self):
        total = self.model.query.count()
        online = self.model.query.filter_by(status=WorkerHealth.ONLINE).count()
        offline = self.model.query.filter_by(status=WorkerHealth.OFFLINE).count()
        degraded = self.model.query.filter_by(status=WorkerHealth.DEGRADED).count()
        total_processed = db.session.query(db.func.sum(WorkerHealth.processed_jobs_count)).scalar() or 0
        total_failed = db.session.query(db.func.sum(WorkerHealth.failed_jobs_count)).scalar() or 0
        active_jobs = db.session.query(db.func.sum(WorkerHealth.active_jobs)).scalar() or 0
        return {
            'total': total, 'online': online, 'offline': offline, 'degraded': degraded,
            'total_processed': total_processed, 'total_failed': total_failed,
            'active_jobs': active_jobs,
        }
