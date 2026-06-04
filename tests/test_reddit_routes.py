def test_new_analysis_page_has_platform_tabs(logged_in_client):
    response = logged_in_client.get('/analysis/new')
    assert response.status_code == 200
    assert b'YouTube' in response.data
    assert b'Reddit' in response.data


def test_reddit_analysis_result(logged_in_client, reddit_analysis):
    response = logged_in_client.get(f'/analysis/{reddit_analysis.id}')
    assert response.status_code == 200
    assert b'Analysis Results' in response.data or b'Comments' in response.data


def test_reddit_analysis_result_shows_metadata(logged_in_client, reddit_analysis):
    response = logged_in_client.get(f'/analysis/{reddit_analysis.id}')
    assert b'Test Reddit Post' in response.data
    assert b'technology' in response.data or b'r/' in response.data


def test_reddit_analysis_post(logged_in_client):
    response = logged_in_client.post('/analysis/new', data={
        'platform': 'reddit',
        'reddit_input': 'abc123',
        'comment_limit': 100,
    })
    assert response.status_code == 302


def test_reddit_analysis_empty_input(logged_in_client):
    response = logged_in_client.post('/analysis/new', data={
        'platform': 'reddit',
        'reddit_input': '',
    })
    assert response.status_code == 200
    assert b'Please enter' in response.data


def test_dashboard_shows_reddit_analysis(logged_in_client, reddit_analysis):
    response = logged_in_client.get('/dashboard/')
    assert response.status_code == 200
    assert b'Reddit' in response.data or b'Test Reddit Post' in response.data


def test_dashboard_platform_filter_all(logged_in_client, analysis, reddit_analysis):
    response = logged_in_client.get('/dashboard/?platform=all')
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_dashboard_platform_filter_youtube(logged_in_client, analysis):
    response = logged_in_client.get('/dashboard/?platform=youtube')
    assert response.status_code == 200


def test_dashboard_platform_filter_reddit(logged_in_client, reddit_analysis):
    response = logged_in_client.get('/dashboard/?platform=reddit')
    assert response.status_code == 200


def test_history_shows_reddit_analysis(logged_in_client, reddit_analysis):
    response = logged_in_client.get('/analysis/history')
    assert response.status_code == 200
    assert b'Reddit' in response.data or b'Test Reddit Post' in response.data
