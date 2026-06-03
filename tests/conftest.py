import pytest
from datetime import datetime, timezone
from app import create_app
from database import db as _db
from models.user import User
from models.analysis import Analysis, YouTubeAnalysis
from models.comment_result import CommentResult
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='function')
def app():
    application = create_app('testing')
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def user(app, db):
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('TestPass123'),
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def logged_in_client(client, user):
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'TestPass123',
    })
    return client


@pytest.fixture
def analysis(app, db, user):
    a = Analysis(user_id=user.id, analysis_type='youtube')
    db.session.add(a)
    db.session.commit()

    yt = YouTubeAnalysis(
        analysis_id=a.id,
        video_id='dQw4w9WgXcQ',
        video_title='Test Video',
        video_description='A test video description.',
        channel_name='Test Channel',
        published_at=datetime(2024, 1, 15, tzinfo=timezone.utc),
        view_count=100000,
        like_count=5000,
        comment_count=2,
        comment_limit=100,
        is_demo=True,
    )
    db.session.add(yt)

    for i, (text, author) in enumerate([
        ('Great video! Very informative.', 'User1'),
        ('BUY NOW!!! Limited offer!!!', 'Spammer'),
    ]):
        c = CommentResult(
            analysis_id=a.id,
            comment_text=text,
            author=author,
            published_at=datetime(2024, 1, 16, tzinfo=timezone.utc) if i == 0 else datetime(2024, 1, 17, tzinfo=timezone.utc),
            spam_score=10.0 if i == 0 else 80.0,
            toxicity_score=5.0,
            sentiment='Positive' if i == 0 else 'Neutral',
            sentiment_score=75.0 if i == 0 else 50.0,
            duplicate_score=0.0,
            ai_like_score=5.0,
            bot_score=0.0,
            risk_score=15.0 if i == 0 else 70.0,
            risk_level='Low' if i == 0 else 'High',
            risk_explanation='Low risk' if i == 0 else 'High risk',
        )
        db.session.add(c)

    db.session.commit()
    return a
