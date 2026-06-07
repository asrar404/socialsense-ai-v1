from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from services.activity_service import ActivityService

activity_bp = Blueprint('activity', __name__, url_prefix='/activity')
activity_service = ActivityService()


@activity_bp.route('')
@activity_bp.route('/')
@login_required
def timeline():
    logs = activity_service.get_user_activity(current_user.id)
    return render_template('activity/timeline.html', logs=logs)


@activity_bp.route('/data')
@login_required
def data():
    logs = activity_service.get_user_activity(current_user.id)
    return jsonify([{
        'id': l.id, 'action': l.action, 'description': l.description,
        'resource_type': l.resource_type, 'resource_id': l.resource_id,
        'created_at': l.created_at.isoformat() if l.created_at else None,
    } for l in logs])
