def test_demo_service_get_video_info():
    from services.demo_service import DemoService
    demo = DemoService()
    info = demo.get_video_info()
    assert 'video_id' in info
    assert 'title' in info
    assert 'channel' in info
    assert info['is_demo'] is True


def test_demo_service_get_comments():
    from services.demo_service import DemoService
    demo = DemoService()
    comments = demo.get_comments()
    assert len(comments) > 0
    assert 'text' in comments[0]
    assert 'author' in comments[0]


def test_demo_analysis_in_dashboard(logged_in_client, analysis):
    response = logged_in_client.get('/analysis/history')
    assert response.status_code == 200


def test_analysis_with_demo_flag(app, db, user, analysis):
    assert analysis.youtube_analysis.is_demo is True


def test_demo_mode_banner(client, app):
    with app.app_context():
        app.config['YOUTUBE_API_KEY'] = ''
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode()
    assert 'Demo Mode' in html or 'demo' in html.lower()
