from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from services.trend_service import TrendService

trend_bp = Blueprint('trends', __name__, url_prefix='/trends')
trend_service = TrendService()


@trend_bp.route('')
@trend_bp.route('/')
@login_required
def index():
    days = request.args.get('days', 30, type=int)
    platform = request.args.get('platform', 'all')
    if days not in (1, 7, 30, 0):
        days = 30
    data = trend_service.get_trends(current_user.id, days=days if days > 0 else 365*10, platform=platform)
    return render_template('trends/index.html', data=data, days=days, platform=platform)


@trend_bp.route('/data')
@login_required
def trend_data():
    days = request.args.get('days', 30, type=int)
    platform = request.args.get('platform', 'all')
    if days not in (1, 7, 30, 0):
        days = 30
    data = trend_service.get_trends(current_user.id, days=days if days > 0 else 365*10, platform=platform)
    return jsonify(data)
