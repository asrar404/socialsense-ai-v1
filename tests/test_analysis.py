def test_video_id_extraction():
    from services.youtube_service import YouTubeService

    assert YouTubeService.extract_video_id('dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('https://youtu.be/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('https://www.youtube.com/embed/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('https://www.youtube.com/shorts/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('') is None
    assert YouTubeService.extract_video_id('not-a-valid-id-here') is None


def test_analysis_creation(logged_in_client):
    response = logged_in_client.post('/analysis/new', data={
        'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    })
    assert response.status_code == 302


def test_analysis_empty_url(logged_in_client):
    response = logged_in_client.post('/analysis/new', data={
        'video_url': '',
    })
    assert response.status_code == 200
    assert b'Please enter' in response.data


def test_analysis_invalid_url(logged_in_client):
    response = logged_in_client.post('/analysis/new', data={
        'video_url': 'not-a-valid-url',
    })
    assert response.status_code == 200
    assert b'Invalid' in response.data or b'Please' in response.data


def test_demo_mode_check(client, app):
    with app.app_context():
        app.config['YOUTUBE_API_KEY'] = ''
    response = client.get('/analysis/api/check-demo')
    assert response.status_code == 200
    data = response.get_json()
    assert data['is_demo'] is True
