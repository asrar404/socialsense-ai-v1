from database import db
from models.job_log import JobLog
from repositories.base import BaseRepository


class JobLogRepository(BaseRepository):
    def __init__(self):
        super().__init__(JobLog)

    def create_log(self, job_id, level, message, step=None, metadata_json=None):
        log = JobLog(
            job_id=job_id,
            level=level,
            step=step,
            message=message,
            metadata_json=metadata_json,
        )
        db.session.add(log)
        db.session.commit()
        return log

    def get_logs(self, job_id, limit=100):
        return self.model.query.filter_by(job_id=job_id).order_by(JobLog.timestamp.asc()).limit(limit).all()

    def get_logs_by_level(self, job_id, level):
        return self.model.query.filter_by(job_id=job_id, level=level).order_by(JobLog.timestamp.asc()).all()
