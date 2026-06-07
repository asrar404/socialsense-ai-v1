from repositories.job_repository import JobRepository
from repositories.worker_health_repository import WorkerHealthRepository
from datetime import datetime, timezone, timedelta


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class MonitoringService:
    def __init__(self):
        self.job_repo = JobRepository()
        self.worker_repo = WorkerHealthRepository()

    def get_dashboard_stats(self):
        from models.job import Job
        pending = self.job_repo.count_all_by_status(Job.PENDING)
        running = self.job_repo.count_all_by_status(Job.RUNNING)
        completed = self.job_repo.count_all_by_status(Job.COMPLETED)
        failed = self.job_repo.count_all_by_status(Job.FAILED)
        cancelled = self.job_repo.count_all_by_status(Job.CANCELLED)
        total = pending + running + completed + failed + cancelled

        success_rate = round((completed / total * 100) if total > 0 else 0, 1)
        failure_rate = round((failed / total * 100) if total > 0 else 0, 1)

        from database import db
        from models.job import Job
        from sqlalchemy import func

        avg_exec = db.session.query(func.avg(Job.execution_time_seconds)).filter(
            Job.status == Job.COMPLETED, Job.execution_time_seconds.isnot(None)
        ).scalar() or 0

        last_24h = _now() - timedelta(hours=24)
        created_24h = Job.query.filter(Job.created_at >= last_24h).count()
        completed_24h = Job.query.filter(
            Job.status == Job.COMPLETED, Job.completed_at >= last_24h
        ).count()

        from models.job import Job
        yt_count = Job.query.filter_by(platform='youtube').count()
        reddit_count = Job.query.filter_by(platform='reddit').count()

        worker_summary = self.worker_repo.get_summary()

        return {
            'pending': pending, 'running': running, 'completed': completed,
            'failed': failed, 'cancelled': cancelled, 'total': total,
            'success_rate': success_rate, 'failure_rate': failure_rate,
            'avg_execution_time': round(avg_exec, 1),
            'created_24h': created_24h, 'completed_24h': completed_24h,
            'youtube_jobs': yt_count, 'reddit_jobs': reddit_count,
        } | {f'worker_{k}': v for k, v in worker_summary.items()}
