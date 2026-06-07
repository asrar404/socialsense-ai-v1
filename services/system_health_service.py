from flask import current_app
from repositories.job_repository import JobRepository
from repositories.notification_repository import NotificationRepository
from repositories.activity_log_repository import ActivityLogRepository
from repositories.scheduled_report_repository import ScheduledReportRepository
from services.notification_service import NotificationService


class SystemHealthService:
    def __init__(self):
        self.job_repo = JobRepository()
        self.notification_repo = NotificationRepository()

    def get_health(self):
        from database import db
        db_ok = True
        try:
            db.session.execute(db.text('SELECT 1'))
        except Exception:
            db_ok = False

        from models.job import Job
        pending = self.job_repo.count_all_by_status(Job.PENDING)
        running = self.job_repo.count_all_by_status(Job.RUNNING)
        failed = self.job_repo.count_all_by_status(Job.FAILED)

        from models.job import Job
        latest = Job.query.order_by(Job.created_at.desc()).first()

        app = current_app._get_current_object() if current_app else None
        yt_key = bool(app.config.get('YOUTUBE_API_KEY')) if app else False
        reddit_id = bool(app.config.get('REDDIT_CLIENT_ID')) if app else False
        reddit_secret = bool(app.config.get('REDDIT_CLIENT_SECRET')) if app else False

        return {
            'database': 'connected' if db_ok else 'error',
            'worker_status': 'active' if running > 0 else 'idle',
            'pending_jobs': pending,
            'running_jobs': running,
            'failed_jobs': failed,
            'latest_job_id': latest.id if latest else None,
            'latest_job_status': latest.status if latest else None,
            'app_version': '6.0',
            'environment': app.config.get('ENV', 'development') if app else 'unknown',
            'youtube_api': 'configured' if yt_key else 'missing',
            'reddit_api': 'configured' if (reddit_id and reddit_secret) else 'missing',
        }


class MaintenanceService:
    def __init__(self):
        self.job_repo = JobRepository()
        self.notification_service = NotificationService()
        self.activity_repo = ActivityLogRepository()
        self.report_repo = ScheduledReportRepository()

    def cleanup_all(self, app):
        from flask import current_app
        config = app.config if app else current_app.config if current_app else {}
        job_days = config.get('JOB_LOG_RETENTION_DAYS', 30)
        notif_days = config.get('NOTIFICATION_RETENTION_DAYS', 30)
        report_days = config.get('REPORT_RETENTION_DAYS', 30)

        results = {}
        results['job_logs'] = self.activity_repo.delete_old_logs(days=job_days)
        results['notifications'] = self.notification_service.cleanup_old(days=notif_days)
        results['reports'] = self.report_repo.delete_old_reports(days=report_days)
        results['jobs'] = self.job_repo.cleanup_old_jobs(days=job_days)
        return results
