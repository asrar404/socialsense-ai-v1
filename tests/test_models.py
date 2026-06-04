from datetime import datetime, timezone


def test_create_user(app, db):
    from models.user import User
    from werkzeug.security import generate_password_hash

    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('TestPass123'),
    )
    db.session.add(user)
    db.session.commit()

    assert user.id is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'


def test_create_analysis(app, db, user):
    from models.analysis import Analysis

    analysis = Analysis(user_id=user.id, analysis_type='youtube')
    db.session.add(analysis)
    db.session.commit()

    assert analysis.id is not None
    assert analysis.user_id == user.id
    assert analysis.analysis_type == 'youtube'


def test_create_youtube_analysis(app, db, user):
    from models.analysis import Analysis, YouTubeAnalysis

    analysis = Analysis(user_id=user.id, analysis_type='youtube')
    db.session.add(analysis)
    db.session.commit()

    yt = YouTubeAnalysis(
        analysis_id=analysis.id,
        video_id='dQw4w9WgXcQ',
        video_title='Test Video',
        video_description='Test desc',
        channel_name='Test Channel',
        published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        view_count=1000,
        like_count=100,
        comment_limit=100,
        is_demo=True,
    )
    db.session.add(yt)
    db.session.commit()

    assert yt.id is not None
    assert yt.video_id == 'dQw4w9WgXcQ'
    assert yt.view_count == 1000
    assert yt.like_count == 100
    assert yt.comment_limit == 100
    assert yt.video_description == 'Test desc'
    assert yt.published_at is not None


def test_create_comment_result(app, db, user, analysis):
    from models.comment_result import CommentResult

    c = CommentResult(
        analysis_id=analysis.id,
        comment_text='Test comment',
        author='TestUser',
        published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        spam_score=10.0,
        toxicity_score=5.0,
        sentiment='Positive',
        risk_score=15.0,
        risk_level='Low',
    )
    db.session.add(c)
    db.session.commit()

    assert c.id is not None
    assert c.comment_text == 'Test comment'
    assert c.risk_level == 'Low'
    assert c.published_at is not None


def test_create_report_export(app, db, analysis):
    from models.report_export import ReportExport

    export = ReportExport(
        analysis_id=analysis.id,
        format_type='csv',
        file_path='/tmp/test.csv',
    )
    db.session.add(export)
    db.session.commit()

    assert export.id is not None
    assert export.format_type == 'csv'


def test_user_analyses_relationship(app, db, user, analysis):
    assert len(user.analyses.all()) >= 1
    assert analysis in user.analyses.all()


def test_analysis_comment_results_relationship(app, db, analysis):
    assert analysis.comment_results.count() == 2


def test_analysis_youtube_relationship(app, db, analysis):
    assert analysis.youtube_analysis is not None
    assert analysis.youtube_analysis.video_id == 'dQw4w9WgXcQ'
    assert analysis.youtube_analysis.view_count == 100000
    assert analysis.youtube_analysis.comment_limit == 100


def test_create_reddit_analysis(app, db, user):
    from models.analysis import Analysis
    from models.reddit_analysis import RedditAnalysis

    analysis = Analysis(user_id=user.id, analysis_type='reddit')
    db.session.add(analysis)
    db.session.commit()

    ra = RedditAnalysis(
        analysis_id=analysis.id,
        post_id='abc123',
        subreddit='technology',
        post_title='Test Post',
        post_body='Test body',
        post_author='TestAuthor',
        post_score=1000,
        upvote_ratio=0.9,
        comment_limit=100,
        is_demo=True,
    )
    db.session.add(ra)
    db.session.commit()

    assert ra.id is not None
    assert ra.post_id == 'abc123'
    assert ra.subreddit == 'technology'
    assert ra.post_score == 1000
    assert ra.upvote_ratio == 0.9
    assert ra.comment_limit == 100


def test_analysis_reddit_relationship(app, db, reddit_analysis):
    assert reddit_analysis.reddit_analysis is not None
    assert reddit_analysis.reddit_analysis.post_id == 'abc123'
    assert reddit_analysis.reddit_analysis.subreddit == 'technology'
    assert reddit_analysis.reddit_analysis.post_score == 5000

def test_reddit_analysis_repr(app, db, reddit_analysis):
    ra = reddit_analysis.reddit_analysis
    assert 'RedditAnalysis' in repr(ra)
    assert 'technology' in repr(ra)
    assert 'abc123' in repr(ra)
