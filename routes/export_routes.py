from flask import Blueprint, send_file, flash, redirect, url_for, jsonify, Response
from flask_login import login_required, current_user
from services.export_service import ExportService
import io

export_bp = Blueprint('export', __name__, url_prefix='/export')
export_service = ExportService()


@export_bp.route('/csv/<int:analysis_id>')
@login_required
def csv_download(analysis_id):
    result = export_service.generate_csv(analysis_id, current_user.id)
    if not result:
        flash('Analysis not found or access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    buffer = io.BytesIO(result['csv_content'].encode('utf-8'))
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=result['filename'],
    )


@export_bp.route('/json/<int:analysis_id>')
@login_required
def json_download(analysis_id):
    result = export_service.generate_json(analysis_id, current_user.id)
    if not result:
        flash('Analysis not found or access denied.', 'danger')
        return redirect(url_for('dashboard.index'))

    return Response(
        result['json_content'],
        mimetype='application/json',
        headers={'Content-Disposition': f'attachment; filename={result["filename"]}'},
    )
