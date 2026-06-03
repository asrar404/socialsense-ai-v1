def test_dashboard_no_analyses(logged_in_client):
    response = logged_in_client.get('/dashboard/')
    assert response.status_code == 200
    assert b'Dashboard' in response.data


def test_dashboard_with_analyses(logged_in_client, analysis):
    response = logged_in_client.get('/dashboard/')
    assert response.status_code == 200
    assert b'Test Video' in response.data or b'Total Analyses' in response.data


def test_dashboard_shows_stats(logged_in_client, analysis):
    response = logged_in_client.get('/dashboard/')
    content = response.data.decode()
    assert 'Total Analyses' in content or 'Comments Processed' in content


def test_dashboard_has_recent_table(logged_in_client, analysis):
    response = logged_in_client.get('/dashboard/')
    assert b'Recent Analyses' in response.data or b'View All' in response.data


def test_dashboard_charts_exist(logged_in_client, analysis):
    response = logged_in_client.get('/dashboard/')
    assert b'riskDistributionChart' in response.data or b'Risk Distribution' in response.data
    assert b'sentimentChart' in response.data or b'Sentiment Distribution' in response.data


def test_history_page(logged_in_client, analysis):
    response = logged_in_client.get('/analysis/history')
    assert b'Test Video' in response.data


def test_history_page_shows_risk_score(logged_in_client, analysis):
    response = logged_in_client.get('/analysis/history')
    assert b'Avg Risk' in response.data or b'danger' in response.data or b'success' in response.data
