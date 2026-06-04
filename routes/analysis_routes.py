from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from services.analysis_service import AnalysisService
from services.reddit_service import RedditService

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')
analysis_service = AnalysisService()
reddit_service = RedditService()


@analysis_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        platform = request.form.get('platform', 'youtube')

        if platform == 'reddit':
            reddit_input = request.form.get('reddit_input', '').strip()
            if not reddit_input:
                flash('Please enter a Reddit post URL, post ID, or subreddit name.', 'danger')
                return render_template('analysis/new.html')

            comment_limit = request.form.get('comment_limit', '100', type=int)
            if comment_limit not in (100, 500, 1000):
                comment_limit = 100

            post_id = reddit_service.extract_post_id(reddit_input)
            if not post_id:
                flash('Invalid Reddit post URL or ID.', 'danger')
                return render_template('analysis/new.html')

            subreddit = reddit_service.extract_post_info(reddit_input)
            subreddit_name = subreddit['subreddit'] if subreddit else None

            result = analysis_service.create_reddit_analysis(
                current_user.id, post_id, subreddit=subreddit_name,
                input_type='post', comment_limit=comment_limit
            )

            if not result['success']:
                flash(result['error'], 'danger')
                return render_template('analysis/new.html')

            flash(f'Reddit analysis complete! Processed {result["comment_count"]} comments.', 'success')
            return redirect(url_for('analysis.result', analysis_id=result['analysis_id']))
        else:
            video_url = request.form.get('video_url', '').strip()
            if not video_url:
                flash('Please enter a YouTube URL or Video ID.', 'danger')
                return render_template('analysis/new.html')

            comment_limit = request.form.get('comment_limit', '100', type=int)
            if comment_limit not in (100, 500, 1000):
                comment_limit = 100

            result = analysis_service.create_youtube_analysis(
                current_user.id, video_url, comment_limit=comment_limit
            )

            if not result['success']:
                flash(result['error'], 'danger')
                return render_template('analysis/new.html')

            flash(f'Analysis complete! Processed {result["comment_count"]} comments.', 'success')
            return redirect(url_for('analysis.result', analysis_id=result['analysis_id']))

    from flask import current_app
    yt_demo = not current_app.config.get('YOUTUBE_API_KEY', '')
    has_reddit = bool(current_app.config.get('REDDIT_CLIENT_ID', '') and current_app.config.get('REDDIT_CLIENT_SECRET', ''))
    return render_template('analysis/new.html', is_demo=yt_demo, has_reddit_creds=has_reddit)


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
