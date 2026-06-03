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
        channel_name='Test Channel',
        is_demo=True,
    )
    db.session.add(yt)
    db.session.commit()

    assert yt.id is not None
    assert yt.video_id == 'dQw4w9WgXcQ'
    assert yt.analysis_id == analysis.id


def test_create_comment_result(app, db, user, analysis):
    from models.comment_result import CommentResult

    c = CommentResult(
        analysis_id=analysis.id,
        comment_text='Test comment',
        author='TestUser',
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
