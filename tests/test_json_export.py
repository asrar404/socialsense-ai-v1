import json


def test_json_export_requires_login(client, analysis):
    response = client.get(f'/export/json/{analysis.id}')
    assert response.status_code == 302


def test_json_export_success(logged_in_client, analysis):
    response = logged_in_client.get(f'/export/json/{analysis.id}')
    assert response.status_code == 200
    assert 'application/json' in response.mimetype


def test_json_content_structure(logged_in_client, analysis):
    response = logged_in_client.get(f'/export/json/{analysis.id}')
    data = json.loads(response.data)

    assert 'exported_at' in data
    assert 'analysis_id' in data
    assert data['analysis_id'] == analysis.id
    assert 'metadata' in data
    assert 'comments' in data
    assert 'comment_count' in data
    assert data['comment_count'] >= 2


def test_json_has_video_metadata(logged_in_client, analysis):
    response = logged_in_client.get(f'/export/json/{analysis.id}')
    data = json.loads(response.data)
    meta = data['metadata']
    assert meta['platform'] == 'youtube'
    assert meta['video_id'] == 'dQw4w9WgXcQ'
    assert meta['title'] == 'Test Video'
    assert meta['view_count'] == 100000
    assert meta['is_demo'] is True


def test_json_has_comment_details(logged_in_client, analysis):
    response = logged_in_client.get(f'/export/json/{analysis.id}')
    data = json.loads(response.data)
    comment = data['comments'][0]
    assert 'comment_text' in comment
    assert 'author' in comment
    assert 'risk_score' in comment
    assert 'risk_level' in comment
    assert 'spam_score' in comment
    assert 'toxicity_score' in comment
    assert 'sentiment' in comment


def test_json_export_not_found(logged_in_client):
    response = logged_in_client.get('/export/json/999')
    assert response.status_code == 302


def test_export_service_generate_json(app, analysis):
    from services.export_service import ExportService
    from database import db

    with app.app_context():
        user = db.session.get(type(analysis.user), analysis.user_id)
        if user:
            result = ExportService().generate_json(analysis.id, user.id)
            assert result is not None
            assert 'json_content' in result
            assert 'filename' in result
            assert result['filename'].endswith('.json')
            data = json.loads(result['json_content'])
            assert data['comment_count'] >= 2


def test_export_service_json_unauthorized(app, analysis):
    from services.export_service import ExportService
    result = ExportService().generate_json(analysis.id, 999)
    assert result is None


def test_reddit_json_export_requires_login(client, reddit_analysis):
    response = client.get(f'/export/json/{reddit_analysis.id}')
    assert response.status_code == 302


def test_reddit_json_export_success(logged_in_client, reddit_analysis):
    response = logged_in_client.get(f'/export/json/{reddit_analysis.id}')
    assert response.status_code == 200
    assert 'application/json' in response.mimetype


def test_reddit_json_content_structure(logged_in_client, reddit_analysis):
    import json
    response = logged_in_client.get(f'/export/json/{reddit_analysis.id}')
    data = json.loads(response.data)

    assert 'exported_at' in data
    assert 'analysis_id' in data
    assert data['analysis_id'] == reddit_analysis.id
    assert 'metadata' in data
    assert data['metadata']['platform'] == 'reddit'
    assert 'comments' in data
    assert 'comment_count' in data


def test_reddit_json_has_post_metadata(logged_in_client, reddit_analysis):
    import json
    response = logged_in_client.get(f'/export/json/{reddit_analysis.id}')
    data = json.loads(response.data)
    meta = data['metadata']
    assert meta['post_id'] == 'abc123'
    assert meta['title'] == 'Test Reddit Post'
    assert meta['score'] == 5000
    assert meta['is_demo'] is True
