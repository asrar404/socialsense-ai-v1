from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from services.analysis_service import AnalysisService
from services.job_service import JobService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
analysis_service = AnalysisService()
job_service = JobService()


@dashboard_bp.route('/')
@login_required
def index():
    platform = request.args.get('platform', 'all')
    if platform not in ('all', 'youtube', 'reddit'):
        platform = 'all'
    stats = analysis_service.get_dashboard_stats(current_user.id, platform=platform)
    recent = analysis_service.get_all_user_analyses_with_data(current_user.id, limit=10)
    job_stats = job_service.get_dashboard_metrics(current_user.id)

    return render_template('dashboard/dashboard.html', stats=stats, analyses=recent, current_platform=platform, job_stats=job_stats)
