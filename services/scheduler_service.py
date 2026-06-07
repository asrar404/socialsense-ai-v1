from repositories.scheduled_analysis_repository import ScheduledAnalysisRepository
from repositories.job_repository import JobRepository
from repositories.notification_repository import NotificationRepository
from services.job_service import JobService
from models.notification import Notification
from database import db
from datetime import datetime, timezone, timedelta


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class SchedulerService:
    def __init__(self):
        self.schedule_repo = ScheduledAnalysisRepository()
        self.job_repo = JobRepository()
        self.notification_repo = NotificationRepository()
        self.job_service = JobService()

    def create_schedule(self, user_id, platform, source_input, frequency, comment_limit=100):
        from models.scheduled_analysis import ScheduledAnalysis
        if platform in ('youtube', 'reddit'):
            source_type = 'url'
        else:
            source_type = platform
        next_run = _now()
        if frequency == ScheduledAnalysis.FREQ_DAILY:
            next_run = _now() + timedelta(days=1)
        elif frequency == ScheduledAnalysis.FREQ_WEEKLY:
            next_run = _now() + timedelta(weeks=1)
        elif frequency == ScheduledAnalysis.FREQ_MONTHLY:
            next_run = _now() + timedelta(days=30)
        schedule = self.schedule_repo.create(
            user_id=user_id, platform=platform, source_type=source_type,
            source_input=source_input, comment_limit=comment_limit,
            frequency=frequency, next_run_at=next_run,
        )
        self.notification_repo.create_notification(
            user_id, Notification.TYPE_SCHEDULE_CREATED,
            'Schedule Created',
            f'Scheduled {frequency} analysis for {source_input}',
            Notification.SEVERITY_INFO,
        )
        return schedule

    def process_due_schedules(self, app):
        due = self.schedule_repo.get_due_schedules()
        count = 0
        for schedule in due:
            request_hash = self.job_service.compute_request_hash(
                schedule.user_id, schedule.platform, schedule.source_input
            )
            existing = self.job_repo.get_job_by_hash(request_hash)
            if existing and existing.status in ('PENDING', 'RUNNING'):
                continue
            result = self.job_service.create_job(
                schedule.user_id, schedule.platform,
                schedule.source_input, schedule.comment_limit, request_hash,
            )
            if result['success']:
                self.schedule_repo.update_next_run(schedule.id)
                count += 1
        return count

    def pause_schedule(self, schedule_id, user_id):
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule or schedule.user_id != user_id:
            return None
        schedule.is_active = False
        db.session.commit()
        return schedule

    def resume_schedule(self, schedule_id, user_id):
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule or schedule.user_id != user_id:
            return None
        schedule.is_active = True
        if not schedule.next_run_at:
            schedule.next_run_at = _now()
        db.session.commit()
        return schedule

    def delete_schedule(self, schedule_id, user_id):
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule or schedule.user_id != user_id:
            return None
        db.session.delete(schedule)
        db.session.commit()
        return True
