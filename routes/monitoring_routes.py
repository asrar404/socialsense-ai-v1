from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from services.monitoring_service import MonitoringService

monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/admin')
monitoring_service = MonitoringService()


@monitoring_bp.route('/monitoring')
@login_required
def dashboard():
    stats = monitoring_service.get_dashboard_stats()
    return render_template('admin/monitoring.html', stats=stats)


@monitoring_bp.route('/monitoring/data')
@login_required
def data():
    stats = monitoring_service.get_dashboard_stats()
    return jsonify(stats)


@monitoring_bp.route('/health')
@login_required
def health():
    from services.system_health_service import SystemHealthService
    svc = SystemHealthService()
    data = svc.get_health()
    return render_template('admin/health.html', health=data)
