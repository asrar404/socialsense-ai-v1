def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'SocialSense' in response.data


def test_dashboard_redirects_when_not_logged_in(client):
    response = client.get('/dashboard/')
    assert response.status_code == 302


def test_dashboard_page(logged_in_client):
    response = logged_in_client.get('/dashboard/')
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_new_analysis_page(logged_in_client):
    response = logged_in_client.get('/analysis/new')
    assert response.status_code == 200
    assert b'Analyze YouTube' in response.data


def test_analysis_result(logged_in_client, analysis):
    response = logged_in_client.get(f'/analysis/{analysis.id}')
    assert response.status_code == 200
    assert b'Analysis Results' in response.data or b'Comments' in response.data


def test_analysis_history(logged_in_client, analysis):
    response = logged_in_client.get('/analysis/history')
    assert response.status_code == 200
    assert b'History' in response.data or b'Test Video' in response.data


def test_analysis_not_found(logged_in_client):
    response = logged_in_client.get('/analysis/999')
    assert response.status_code == 302


def test_404_error(client):
    response = client.get('/nonexistent-page')
    assert response.status_code == 404
