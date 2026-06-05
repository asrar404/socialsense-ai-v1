import pytest
from datetime import datetime, timezone, timedelta


class TestJobModel:
    def test_create_job(self, app, db, user):
        from models.job import Job
        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ',
            comment_limit=100,
            request_hash='abc123',
        )
        db.session.add(job)
        db.session.commit()

        assert job.id is not None
        assert job.status == 'PENDING'
        assert job.progress_percent == 0
        assert job.retry_count == 0
        assert job.created_at is not None

    def test_job_status_transitions(self, app, db, user):
        from models.job import Job
        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ',
            comment_limit=100,
            request_hash='abc123',
        )
        db.session.add(job)
        db.session.commit()

        job.status = 'RUNNING'
        job.started_at = datetime.now(timezone.utc)
        job.progress_percent = 50
        db.session.commit()

        assert job.status == 'RUNNING'
        assert job.progress_percent == 50

        job.status = 'COMPLETED'
        job.completed_at = datetime.now(timezone.utc)
        job.progress_percent = 100
        db.session.commit()

        assert job.status == 'COMPLETED'
        assert job.progress_percent == 100

    def test_job_error_state(self, app, db, user):
        from models.job import Job
        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ',
            comment_limit=100,
            request_hash='abc123',
        )
        db.session.add(job)
        db.session.commit()

        job.status = 'FAILED'
        job.error_message = 'Something went wrong'
        db.session.commit()

        assert job.status == 'FAILED'
        assert job.error_message == 'Something went wrong'

    def test_job_cancellation_request(self, app, db, user):
        from models.job import Job
        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ',
            comment_limit=100,
            request_hash='abc123',
        )
        db.session.add(job)
        db.session.commit()

        assert job.cancellation_requested is False

        job.cancellation_requested = True
        db.session.commit()

        assert job.cancellation_requested is True

    def test_job_execution_time(self, app, db, user):
        from models.job import Job
        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ',
            comment_limit=100,
            request_hash='abc123',
        )
        db.session.add(job)
        db.session.commit()

        job.execution_time_seconds = 42.5
        db.session.commit()

        assert job.execution_time_seconds == 42.5


class TestJobLogModel:
    def test_create_job_log(self, app, db, user):
        from models.job import Job
        from models.job_log import JobLog
        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ',
            comment_limit=100,
            request_hash='abc123',
        )
        db.session.add(job)
        db.session.commit()

        log = JobLog(job_id=job.id, level='INFO', message='Job started')
        db.session.add(log)
        db.session.commit()

        assert log.id is not None
        assert log.job_id == job.id
        assert log.level == 'INFO'
        assert log.message == 'Job started'
        assert log.timestamp is not None

    def test_multiple_logs_per_job(self, app, db, user):
        from models.job import Job
        from models.job_log import JobLog
        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ',
            comment_limit=100,
            request_hash='abc123',
        )
        db.session.add(job)
        db.session.commit()

        for level, msg in [('INFO', 'Starting'), ('DEBUG', 'Processing comment 1'), ('WARNING', 'Rate limited')]:
            db.session.add(JobLog(job_id=job.id, level=level, message=msg))
        db.session.commit()

        logs = JobLog.query.filter_by(job_id=job.id).order_by(JobLog.id).all()
        assert len(logs) == 3
        assert logs[0].level == 'INFO'
        assert logs[2].level == 'WARNING'

    def test_log_level_defaults(self, app, db, user):
        from models.job import Job
        from models.job_log import JobLog
        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ',
            comment_limit=100,
            request_hash='abc123',
        )
        db.session.add(job)
        db.session.commit()

        log = JobLog(job_id=job.id, message='Test message')
        db.session.add(log)
        db.session.commit()

        assert log.level == 'INFO'


class TestJobRepository:
    def test_create(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ',
            comment_limit=100,
            request_hash='abc123',
        )
        assert job.id is not None
        assert job.user_id == user.id
        assert job.platform == 'youtube'

    def test_get_by_id(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='def456',
        )
        found = repo.get_job(job.id)
        assert found is not None
        assert found.id == job.id

        assert repo.get_job(99999) is None

    def test_get_by_user_and_id(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='ghi789',
        )
        found = repo.get_job(job.id)
        assert found is not None
        assert found.user_id == user.id

    def test_get_user_jobs(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        for i in range(5):
            repo.create_job(
                user_id=user.id, platform='youtube',
                source_type='analysis',
                source_input=f'test{i}', comment_limit=100,
                request_hash=f'hash{i}',
            )
        jobs = repo.get_jobs_for_user(user.id, limit=10)
        assert len(jobs) == 5

        limited = repo.get_jobs_for_user(user.id, limit=3)
        assert len(limited) == 3

    def test_find_by_request_hash(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='unique_hash',
        )
        found = repo.get_job_by_hash('unique_hash')
        assert found is not None

        not_found = repo.get_job_by_hash('nonexistent')
        assert not_found is None

    def test_find_stuck_jobs(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='stuck1',
        )
        job.status = 'RUNNING'
        job.started_at = datetime.now(timezone.utc) - timedelta(hours=2)
        db.session.commit()

        stuck = repo.get_stuck_jobs()
        assert len(stuck) >= 1
        assert stuck[0].id == job.id

    def test_find_stuck_jobs_excludes_finished(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        for st in ['COMPLETED', 'FAILED', 'CANCELLED']:
            j = repo.create_job(
                user_id=user.id, platform='youtube',
                source_type='analysis',
                source_input='test', comment_limit=100,
                request_hash=f'stuck_not_{st}',
            )
            j.status = st
            j.started_at = datetime.now(timezone.utc) - timedelta(hours=2)
        db.session.commit()

        stuck = repo.get_stuck_jobs()
        assert len(stuck) == 0

    def test_update_progress(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='update1',
        )
        updated = repo.update_progress(job.id, 50, step='Processing')
        assert updated.progress_percent == 50
        assert updated.current_step == 'Processing'

    def test_update_status(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='update2',
        )
        updated = repo.update_status(job.id, 'RUNNING')
        assert updated.status == 'RUNNING'

    def test_update_status_not_found(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        result = repo.update_status(99999, 'COMPLETED')
        assert result is None

    def test_mark_completed_with_analysis(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='complete1',
        )
        updated = repo.mark_completed(job.id, analysis_id=42)
        assert updated.status == 'COMPLETED'
        assert updated.result_analysis_id == 42
        assert updated.progress_percent == 100

    def test_mark_failed(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='fail1',
        )
        updated = repo.mark_failed(job.id, error_message='Oops')
        assert updated.status == 'FAILED'
        assert updated.error_message == 'Oops'

    def test_mark_cancelled(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='cancel1',
        )
        updated = repo.mark_cancelled(job.id)
        assert updated.status == 'CANCELLED'

    def test_increment_retry(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='retry1',
        )
        job.retry_count = 0
        db.session.commit()

        updated = repo.increment_retry_count(job.id)
        assert updated.retry_count == 1
        assert updated.status == 'PENDING'

    def test_get_user_job_stats(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        for status in ['COMPLETED', 'COMPLETED', 'FAILED', 'RUNNING', 'PENDING']:
            j = repo.create_job(
                user_id=user.id, platform='youtube',
                source_type='analysis',
                source_input='test', comment_limit=100,
                request_hash=f'stat_{status}_{id({status})}',
            )
            j.status = status
        db.session.commit()

        assert repo.count_by_user_and_status(user.id, 'COMPLETED') >= 2
        assert repo.count_by_user_and_status(user.id, 'FAILED') >= 1
        assert repo.count_by_user_and_status(user.id, 'RUNNING') >= 1

    def test_cleanup_old_jobs(self, app, db, user):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        old = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='old', comment_limit=100, request_hash='old1',
        )
        old.created_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=60)
        old.status = 'COMPLETED'
        db.session.commit()

        recent = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='recent', comment_limit=100, request_hash='recent1',
        )
        recent.status = 'COMPLETED'
        db.session.commit()

        deleted = repo.cleanup_old_jobs(days=30)
        assert deleted == 1

        assert repo.get_job(old.id) is None
        assert repo.get_job(recent.id) is not None


class TestJobLogRepository:
    def test_add_log(self, app, db, user):
        from repositories.job_log_repository import JobLogRepository
        from models.job import Job
        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='log1',
        )
        db.session.add(job)
        db.session.commit()

        repo = JobLogRepository()
        log = repo.create_log(job.id, 'INFO', 'Test message', 'Step')
        assert log.id is not None
        assert log.message == 'Test message'

    def test_get_job_logs(self, app, db, user):
        from repositories.job_log_repository import JobLogRepository
        from models.job import Job
        from models.job_log import JobLog

        job = Job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='log2',
        )
        db.session.add(job)
        db.session.commit()

        for msg in ['First', 'Second', 'Third']:
            db.session.add(JobLog(job_id=job.id, message=msg, level='INFO'))
        db.session.commit()

        repo = JobLogRepository()
        logs = repo.get_logs(job.id)
        assert len(logs) == 3
        assert logs[0].message == 'First'
        assert logs[2].message == 'Third'


class TestJobService:
    def test_create_job(self, app, db, user):
        from services.job_service import JobService
        import threading
        original_start = threading.Thread.start
        threading.Thread.start = lambda self, *a, **kw: None
        try:
            service = JobService()
            result = service.create_job(
                user.id, 'youtube', 'dQw4w9WgXcQ', 100, 'service_hash_1',
            )
            assert result['success'] is True
            assert 'job_id' in result
            assert result['duplicate'] is False
        finally:
            threading.Thread.start = original_start

    def test_duplicate_job_detection(self, app, db, user):
        from services.job_service import JobService
        import threading
        original_start = threading.Thread.start
        threading.Thread.start = lambda self, *a, **kw: None
        try:
            service = JobService()
            result1 = service.create_job(
                user.id, 'youtube', 'dQw4w9WgXcQ', 100, 'service_hash_dup',
            )
            assert result1['success'] is True

            result2 = service.create_job(
                user.id, 'youtube', 'dQw4w9WgXcQ', 100, 'service_hash_dup',
            )
            assert result2['success'] is True
            assert result2['duplicate'] is True
        finally:
            threading.Thread.start = original_start

    def test_get_job(self, app, db, user):
        from services.job_service import JobService
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ', comment_limit=100, request_hash='get_job_test',
        )
        service = JobService()
        found = service.get_job(job.id, user.id)
        assert found is not None
        assert found.platform == 'youtube'

        not_found = service.get_job(99999, user.id)
        assert not_found is None

    def test_get_job_other_user(self, app, db, user):
        from services.job_service import JobService
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='get_other',
        )
        service = JobService()
        result = service.get_job(job.id, user_id=9999)
        assert result is None

    def test_get_jobs_for_user(self, app, db, user):
        from services.job_service import JobService
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        for i in range(3):
            repo.create_job(
                user_id=user.id, platform='youtube', source_type='analysis',
                source_input=f'test{i}', comment_limit=100, request_hash=f'service_hash_user_{i}',
            )

        service = JobService()
        jobs = service.get_jobs_for_user(user.id)
        assert len(jobs) == 3

    def test_get_dashboard_metrics(self, app, db, user):
        from services.job_service import JobService
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        for i in range(5):
            repo.create_job(
                user_id=user.id, platform='youtube', source_type='analysis',
                source_input=f'test{i}', comment_limit=100, request_hash=f'service_hash_metric_{i}',
            )

        service = JobService()
        metrics = service.get_dashboard_metrics(user.id)
        assert metrics['pending'] == 5

    def test_get_job_status(self, app, db, user):
        from services.job_service import JobService
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube', source_type='analysis',
            source_input='dQw4w9WgXcQ', comment_limit=100, request_hash='status_test',
        )

        service = JobService()
        status = service.get_job_status(job.id, user.id)
        assert status is not None
        assert status['status'] == 'PENDING'
        assert status['progress_percent'] == 0

    def test_get_job_status_not_found(self, app, db, user):
        from services.job_service import JobService
        service = JobService()
        assert service.get_job_status(99999, user.id) is None

    def test_cancel_job(self, app, db, user):
        from services.job_service import JobService
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube', source_type='analysis',
            source_input='dQw4w9WgXcQ', comment_limit=100, request_hash='cancel_test',
        )

        service = JobService()
        result = service.cancel_job(job.id, user.id)
        assert result['success'] is True

    def test_cancel_job_not_found(self, app, db, user):
        from services.job_service import JobService
        service = JobService()
        result = service.cancel_job(99999, user.id)
        assert result['success'] is False
        assert 'not found' in result['error']

    def test_retry_failed_job(self, app, db, user):
        from services.job_service import JobService
        from repositories.job_repository import JobRepository
        import threading
        original_start = threading.Thread.start
        threading.Thread.start = lambda self, *a, **kw: None
        try:
            repo = JobRepository()
            job = repo.create_job(
                user_id=user.id, platform='youtube', source_type='analysis',
                source_input='test', comment_limit=100, request_hash='retry_test',
            )
            repo.mark_failed(job.id, error_message='Test error')

            service = JobService()
            result = service.retry_job(job.id, user.id)
            assert result['success'] is True
        finally:
            threading.Thread.start = original_start

    def test_retry_pending_job_fails(self, app, db, user):
        from services.job_service import JobService
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id, platform='youtube', source_type='analysis',
            source_input='test', comment_limit=100, request_hash='retry_pending_test',
        )

        service = JobService()
        result = service.retry_job(job.id, user.id)
        assert result['success'] is False

    def test_compute_request_hash(self, app, db):
        from services.job_service import JobService
        service = JobService()

        hash1 = service.compute_request_hash(1, 'youtube', 'dQw4w9WgXcQ')
        hash2 = service.compute_request_hash(1, 'youtube', 'dQw4w9WgXcQ')
        hash3 = service.compute_request_hash(1, 'reddit', 'dQw4w9WgXcQ')

        assert hash1 == hash2
        assert hash1 != hash3


class TestJobRoutes:
    def test_job_status_page(self, app, db, user, client):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='dQw4w9WgXcQ', comment_limit=100, request_hash='route1',
        )

        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })

        response = client.get(f'/analysis/jobs/{job.id}')
        assert response.status_code == 200
        assert b'youtube' in response.data
        assert b'PENDING' in response.data

    def test_job_status_not_owned(self, app, db, user, client):
        from models.user import User
        from repositories.job_repository import JobRepository
        from werkzeug.security import generate_password_hash

        other = User(
            username='other', email='other@test.com',
            password_hash=generate_password_hash('OtherPass123'),
        )
        db.session.add(other)
        db.session.commit()

        repo = JobRepository()
        job = repo.create_job(
            user_id=other.id,
            platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='route2',
        )

        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })

        response = client.get(f'/analysis/jobs/{job.id}')
        assert response.status_code == 302

    def test_job_list_page(self, app, db, user, client):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        for i in range(3):
            repo.create_job(
                user_id=user.id,
                platform='youtube',
                source_type='analysis',
                source_input=f'test{i}', comment_limit=100, request_hash=f'route_list_{i}',
            )

        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })

        response = client.get('/analysis/jobs/')
        assert response.status_code == 200
        assert b'youtube' in response.data

    def test_job_list_requires_auth(self, app, db, user, client):
        response = client.get('/analysis/jobs/')
        assert response.status_code == 302

    def test_job_api_status(self, app, db, user, client):
        from repositories.job_repository import JobRepository
        from models.job_log import JobLog

        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='route_api',
        )

        for msg in ['Step 1', 'Step 2']:
            db.session.add(JobLog(job_id=job.id, message=msg, level='INFO'))
        db.session.commit()

        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })

        response = client.get(f'/analysis/jobs/{job.id}/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'PENDING'

    def test_job_api_status_not_owned(self, app, db, user, client):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=9999,
            platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='route_api2',
        )

        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })

        response = client.get(f'/analysis/jobs/{job.id}/status')
        assert response.status_code == 404

    def test_job_api_cancel(self, app, db, user, client):
        from repositories.job_repository import JobRepository
        repo = JobRepository()
        job = repo.create_job(
            user_id=user.id,
            platform='youtube',
            source_type='analysis',
            source_input='test', comment_limit=100, request_hash='route_cancel',
        )

        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })

        response = client.post(f'/analysis/jobs/{job.id}/cancel',
                               headers={'X-Requested-With': 'XMLHttpRequest'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_job_api_cancel_not_found(self, app, db, user, client):
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'TestPass123',
        })

        response = client.post('/analysis/jobs/99999/cancel',
                               headers={'X-Requested-With': 'XMLHttpRequest'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is False

    def test_analysis_form_loads(self, app, db, client):
        response = client.get('/analysis/new')
        assert response.status_code == 302
