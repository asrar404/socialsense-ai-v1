from flask import Blueprint, render_template
from flask_login import login_required, current_user
from services.analysis_service import AnalysisService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
analysis_service = AnalysisService()


@dashboard_bp.route('/')
@login_required
def index():
    stats = analysis_service.get_dashboard_stats(current_user.id)
    recent = analysis_service.get_recent_user_analyses(current_user.id, 10)

    return render_template('dashboard/dashboard.html', stats=stats, analyses=recent)
