import csv
import io


def test_csv_export_requires_login(client, analysis):
    response = client.get(f'/export/csv/{analysis.id}')
    assert response.status_code == 302


def test_csv_export_success(logged_in_client, analysis):
    response = logged_in_client.get(f'/export/csv/{analysis.id}')
    assert response.status_code == 200
    assert 'text/csv' in response.mimetype


def test_csv_content(logged_in_client, analysis):
    response = logged_in_client.get(f'/export/csv/{analysis.id}')
    content = response.data.decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    assert len(rows) > 0
    header_row_found = any('Comment' in row and 'Risk Score' in row for row in rows)
    assert header_row_found, 'CSV should have analysis column headers'
    assert len(rows) > 2


def test_csv_has_video_metadata(logged_in_client, analysis):
    response = logged_in_client.get(f'/export/csv/{analysis.id}')
    content = response.data.decode('utf-8')
    assert 'Video ID' in content
    assert 'dQw4w9WgXcQ' in content
    assert 'Test Video' in content


def test_csv_export_not_found(logged_in_client):
    response = logged_in_client.get('/export/csv/999')
    assert response.status_code == 302


def test_export_service_generate_csv(app, analysis):
    from services.export_service import ExportService
    from database import db

    with app.app_context():
        user = db.session.get(type(analysis.user), analysis.user_id)
        if user:
            result = ExportService().generate_csv(analysis.id, user.id)
            assert result is not None
            assert 'csv_content' in result
            assert 'filename' in result
            assert result['filename'].endswith('.csv')


def test_export_service_unauthorized(app, analysis):
    from services.export_service import ExportService
    result = ExportService().generate_csv(analysis.id, 999)
    assert result is None


def test_reddit_csv_export_requires_login(client, reddit_analysis):
    response = client.get(f'/export/csv/{reddit_analysis.id}')
    assert response.status_code == 302


def test_reddit_csv_export_success(logged_in_client, reddit_analysis):
    response = logged_in_client.get(f'/export/csv/{reddit_analysis.id}')
    assert response.status_code == 200
    assert 'text/csv' in response.mimetype


def test_reddit_csv_has_post_metadata(logged_in_client, reddit_analysis):
    response = logged_in_client.get(f'/export/csv/{reddit_analysis.id}')
    content = response.data.decode('utf-8')
    assert 'Post ID' in content
    assert 'abc123' in content
    assert 'Test Reddit Post' in content


def test_reddit_csv_export_not_found(logged_in_client):
    response = logged_in_client.get('/export/csv/999')
    assert response.status_code == 302


def test_reddit_export_service_generate_csv(app, reddit_analysis):
    from services.export_service import ExportService
    from database import db

    with app.app_context():
        user = db.session.get(type(reddit_analysis.user), reddit_analysis.user_id)
        if user:
            result = ExportService().generate_csv(reddit_analysis.id, user.id)
            assert result is not None
            assert 'csv_content' in result
            assert 'filename' in result
            assert result['filename'].endswith('.csv')
