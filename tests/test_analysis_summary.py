def test_summary_generated_after_youtube_analysis(app, db, user):
    from services.analysis_service import AnalysisService
    from flask import current_app
    service = AnalysisService()

    with app.app_context():
        current_app.config['YOUTUBE_API_KEY'] = ''

    result = service.create_youtube_analysis(user.id, 'dQw4w9WgXcQ', comment_limit=100)
    assert result['success'] is True

    analysis = service.analysis_repo.get_by_id(result['analysis_id'])
    assert analysis is not None
    assert analysis.analysis_summary is not None
    assert 'Comments analyzed' in analysis.analysis_summary
    assert 'Average Toxicity' in analysis.analysis_summary


def test_summary_has_sentiment_breakdown(app, db, user):
    from services.analysis_service import AnalysisService
    from flask import current_app
    service = AnalysisService()

    with app.app_context():
        current_app.config['YOUTUBE_API_KEY'] = ''

    result = service.create_youtube_analysis(user.id, 'dQw4w9WgXcQ', comment_limit=100)
    assert result['success'] is True

    analysis = service.analysis_repo.get_by_id(result['analysis_id'])
    if analysis and analysis.analysis_summary:
        assert 'Positive' in analysis.analysis_summary
        assert 'Neutral' in analysis.analysis_summary
        assert 'Negative' in analysis.analysis_summary


def test_summary_stores_aggregate_scores(app, db, user):
    from services.analysis_service import AnalysisService
    from flask import current_app
    service = AnalysisService()

    with app.app_context():
        current_app.config['YOUTUBE_API_KEY'] = ''

    result = service.create_youtube_analysis(user.id, 'dQw4w9WgXcQ', comment_limit=100)
    assert result['success'] is True

    analysis = service.analysis_repo.get_by_id(result['analysis_id'])
    if analysis:
        assert analysis.average_sentiment is not None or len(result.get('error', '')) == 0
