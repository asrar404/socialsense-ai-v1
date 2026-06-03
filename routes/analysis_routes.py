from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from services.analysis_service import AnalysisService

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')
analysis_service = AnalysisService()


@analysis_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        video_url = request.form.get('video_url', '').strip()
        if not video_url:
            flash('Please enter a YouTube URL or Video ID.', 'danger')
            return render_template('analysis/new.html')

        result = analysis_service.create_youtube_analysis(current_user.id, video_url)

        if not result['success']:
            flash(result['error'], 'danger')
            return render_template('analysis/new.html')

        flash(f'Analysis complete! Processed {result["comment_count"]} comments.', 'success')
        return redirect(url_for('analysis.result', analysis_id=result['analysis_id']))

    is_demo = not __import__('flask', fromlist=['current_app']).current_app.config.get('YOUTUBE_API_KEY', '')
    return render_template('analysis/new.html', is_demo=is_demo)


@analysis_bp.route('/<int:analysis_id>')
@login_required
def result(analysis_id):
    data = analysis_service.get_analysis_results(analysis_id, current_user.id)
    if not data:
        flash('Analysis not found.', 'danger')
        return redirect(url_for('dashboard.index'))

    return render_template('analysis/result.html', data=data)


@analysis_bp.route('/history')
@login_required
def history():
    analyses = analysis_service.get_all_user_analyses_with_data(current_user.id)
    return render_template('analysis/history.html', analyses=analyses)


@analysis_bp.route('/api/check-demo')
def check_demo():
    from flask import current_app
    is_demo = not current_app.config.get('YOUTUBE_API_KEY', '')
    return jsonify({'is_demo': is_demo})
