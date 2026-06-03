import csv
import io


def test_csv_export_requires_login(client, analysis):
    response = client.get(f'/export/csv/{analysis.id}')
    assert response.status_code == 302


def test_csv_export_success(logged_in_client, analysis):
    response = logged_in_client.get(f'/export/csv/{analysis.id}')
    assert response.status_code == 200
    assert 'text/csv' in response.content_type or 'text/csv' in response.mimetype


def test_csv_content(logged_in_client, analysis):
    response = logged_in_client.get(f'/export/csv/{analysis.id}')
    content = response.data.decode('utf-8')
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    assert len(rows) > 0
    assert 'Comment' in rows[0]
    assert 'Risk Score' in rows[0]
    assert len(rows) > 1


def test_csv_export_not_found(logged_in_client):
    response = logged_in_client.get('/export/csv/999')
    assert response.status_code == 302


def test_export_service_generate_csv(app, analysis):
    from services.export_service import ExportService
    from models.user import User

    with app.app_context():
        from database import db
        user = db.session.get(User, analysis.user_id)
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
