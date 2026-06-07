from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from services.notification_service import NotificationService

notification_bp = Blueprint('notifications', __name__, url_prefix='/notifications')
notification_service = NotificationService()


@notification_bp.route('')
@notification_bp.route('/')
@login_required
def list_notifications():
    notifications = notification_service.get_user_notifications(current_user.id)
    unread = notification_service.get_unread_count(current_user.id)
    return render_template('notifications/list.html', notifications=notifications, unread_count=unread)


@notification_bp.route('/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_read(notification_id):
    result = notification_service.mark_as_read(notification_id, current_user.id)
    if not result:
        return jsonify({'error': 'Not found'}), 404
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    return redirect(url_for('notifications.list_notifications'))


@notification_bp.route('/read-all', methods=['POST'])
@login_required
def mark_all_read():
    notification_service.mark_all_read(current_user.id)
    flash('All notifications marked as read.', 'info')
    return redirect(url_for('notifications.list_notifications'))


@notification_bp.route('/api/unread-count')
@login_required
def unread_count():
    count = notification_service.get_unread_count(current_user.id)
    return jsonify({'count': count})
