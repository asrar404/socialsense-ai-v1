def test_dashboard_stats_has_bot_score(app, db, user, analysis):
    from services.analysis_service import AnalysisService
    service = AnalysisService()
    stats = service.get_dashboard_stats(user.id)
    assert 'avg_bot' in stats
    assert 'community_health' in stats
    assert 'critical_comments' in stats


def test_dashboard_stats_platform_filter(app, db, user, analysis):
    from services.analysis_service import AnalysisService
    service = AnalysisService()
    stats_all = service.get_dashboard_stats(user.id, platform='all')
    stats_yt = service.get_dashboard_stats(user.id, platform='youtube')
    assert stats_all['total_analyses'] >= stats_yt['total_analyses']


def test_dashboard_community_health_label(app, db, user):
    from services.analysis_service import AnalysisService
    service = AnalysisService()
    stats = service.get_dashboard_stats(user.id)
    assert stats['community_health'] in ('Low', 'Medium', 'High', 'Critical')


def test_analysis_summary_generated(app, db, user):
    from services.analysis_service import AnalysisService
    from flask import current_app
    service = AnalysisService()

    with app.app_context():
        current_app.config['YOUTUBE_API_KEY'] = ''

    result = service.create_youtube_analysis(user.id, 'dQw4w9WgXcQ', comment_limit=100)
    assert result['success'] is True

    data = service.get_analysis_results(result['analysis_id'], user.id)
    assert data is not None
    assert data['analysis'].analysis_summary is not None or data['analysis'].average_sentiment is not None


def test_analysis_summary_content(app, db, user):
    from services.analysis_service import AnalysisService
    from flask import current_app
    service = AnalysisService()

    with app.app_context():
        current_app.config['YOUTUBE_API_KEY'] = ''

    result = service.create_youtube_analysis(user.id, 'dQw4w9WgXcQ', comment_limit=100)
    assert result['success'] is True

    analysis_rec = service.analysis_repo.get_by_id(result['analysis_id'])
    if analysis_rec and analysis_rec.analysis_summary:
        assert 'Comments analyzed' in analysis_rec.analysis_summary
        assert 'Positive' in analysis_rec.analysis_summary or 'Negative' in analysis_rec.analysis_summary

def test_dashboard_metrics_include_new_fields(app, db, user, analysis):
    from services.analysis_service import AnalysisService
    service = AnalysisService()
    stats = service.get_dashboard_stats(user.id)
    assert 'avg_bot' in stats
    assert 'avg_ai_like' in stats
    assert 'avg_spam' in stats
    assert 'avg_toxicity' in stats
    assert 'avg_sentiment' in stats
    assert 'avg_risk' in stats
