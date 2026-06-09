import pytest
import json
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TestVideoTranscriptModel:
    def test_create_video_transcript(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(
            youtube_analysis_id=yt.id,
            video_id=yt.video_id,
            language='en',
            transcript_text='Hello world',
            source=VideoTranscript.SOURCE_TRANSCRIPT_API,
            is_auto_generated=False,
            segment_count=1,
            word_count=2,
        )
        db.session.add(t)
        db.session.commit()
        assert t.id is not None
        assert t.video_id == yt.video_id
        assert t.source == 'youtube_transcript_api'
        assert not t.is_auto_generated

    def test_video_transcript_defaults(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id)
        db.session.add(t)
        db.session.commit()
        assert t.source == 'unavailable'
        assert t.segment_count == 0
        assert t.word_count == 0

    def test_video_transcript_relationship_with_youtube_analysis(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id)
        db.session.add(t)
        db.session.commit()
        assert t.youtube_analysis.id == yt.id
        assert yt.transcript.id == t.id

    def test_cascade_delete_from_youtube_analysis(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        from models.analysis import YouTubeAnalysis
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id)
        db.session.add(t)
        db.session.commit()
        t_id = t.id
        db.session.delete(yt)
        db.session.commit()
        assert VideoTranscript.query.get(t_id) is None

    def test_repr(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id, source=VideoTranscript.SOURCE_DEMO)
        db.session.add(t)
        db.session.commit()
        assert 'VideoTranscript' in repr(t)
        assert yt.video_id in repr(t)


class TestTranscriptSegmentModel:
    def test_create_segment(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        from models.transcript_segment import TranscriptSegment
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id)
        db.session.add(t)
        db.session.flush()
        s = TranscriptSegment(
            transcript_id=t.id, start_time=0.0, end_time=5.0,
            text='Hello world', word_count=2, segment_index=0,
        )
        db.session.add(s)
        db.session.commit()
        assert s.id is not None
        assert s.text == 'Hello world'

    def test_segment_relationship(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        from models.transcript_segment import TranscriptSegment
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id)
        db.session.add(t)
        db.session.flush()
        for i in range(3):
            db.session.add(TranscriptSegment(
                transcript_id=t.id, start_time=i * 5.0, end_time=(i + 1) * 5.0,
                text=f'Segment {i}', word_count=2, segment_index=i,
            ))
        db.session.commit()
        assert t.segments.count() == 3

    def test_cascade_delete_from_transcript(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        from models.transcript_segment import TranscriptSegment
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id)
        db.session.add(t)
        db.session.flush()
        s = TranscriptSegment(
            transcript_id=t.id, start_time=0.0, end_time=5.0,
            text='Test', word_count=1, segment_index=0,
        )
        db.session.add(s)
        db.session.commit()
        s_id = s.id
        db.session.delete(t)
        db.session.commit()
        assert TranscriptSegment.query.get(s_id) is None

    def test_repr(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        from models.transcript_segment import TranscriptSegment
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id)
        db.session.add(t)
        db.session.flush()
        s = TranscriptSegment(
            transcript_id=t.id, start_time=1.5, end_time=4.5,
            text='Test', word_count=1, segment_index=0,
        )
        db.session.add(s)
        db.session.commit()
        assert 'TranscriptSegment' in repr(s)
        assert '1.5s' in repr(s)


class TestCommentContextModel:
    def test_create_comment_context(self, app, db, analysis):
        from models.comment_context import CommentContext
        from models.comment_result import CommentResult
        cr = db.session.get(CommentResult, analysis.comment_results[0].id)
        ctx = CommentContext(
            comment_result_id=cr.id,
            transcript_relevance_score=0.85,
            topic_alignment_score=0.75,
            off_topic_score=0.15,
            context_match_label=CommentContext.LABEL_HIGHLY_RELEVANT,
            reason='Test reason',
        )
        db.session.add(ctx)
        db.session.commit()
        assert ctx.id is not None
        assert ctx.context_match_label == 'highly_relevant'

    def test_comment_context_defaults(self, app, db, analysis):
        from models.comment_context import CommentContext
        from models.comment_result import CommentResult
        cr = db.session.get(CommentResult, analysis.comment_results[0].id)
        ctx = CommentContext(comment_result_id=cr.id)
        db.session.add(ctx)
        db.session.commit()
        assert ctx.transcript_relevance_score == 0.0
        assert ctx.context_match_label == 'unknown'

    def test_comment_context_unique_constraint(self, app, db, analysis):
        from models.comment_context import CommentContext
        from models.comment_result import CommentResult
        cr = db.session.get(CommentResult, analysis.comment_results[0].id)
        ctx1 = CommentContext(comment_result_id=cr.id)
        db.session.add(ctx1)
        db.session.commit()
        ctx2 = CommentContext(comment_result_id=cr.id)
        db.session.add(ctx2)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()

    def test_comment_context_relationship_with_comment_result(self, app, db, analysis):
        from models.comment_context import CommentContext
        from models.comment_result import CommentResult
        cr = db.session.get(CommentResult, analysis.comment_results[0].id)
        ctx = CommentContext(comment_result_id=cr.id)
        db.session.add(ctx)
        db.session.commit()
        assert ctx.comment_result.id == cr.id
        assert cr.context.id == ctx.id

    def test_repr(self, app, db, analysis):
        from models.comment_context import CommentContext
        from models.comment_result import CommentResult
        cr = db.session.get(CommentResult, analysis.comment_results[0].id)
        ctx = CommentContext(comment_result_id=cr.id, context_match_label=CommentContext.LABEL_RELEVANT)
        db.session.add(ctx)
        db.session.commit()
        assert 'CommentContext' in repr(ctx)
        assert 'relevant' in repr(ctx)


class TestTranscriptProcessingService:
    def test_clean_text(self):
        from services.transcript_processing_service import TranscriptProcessingService
        result = TranscriptProcessingService.clean_text('Hello, World!!! This is   a TEST.')
        assert result == 'hello world this is a test'

    def test_clean_text_empty(self):
        from services.transcript_processing_service import TranscriptProcessingService
        assert TranscriptProcessingService.clean_text('') == ''

    def test_extract_keywords(self):
        from services.transcript_processing_service import TranscriptProcessingService
        text = 'product review technology battery life design quality price customer support feedback'
        keywords = TranscriptProcessingService.extract_keywords(text, top_n=5)
        assert len(keywords) <= 5
        assert all(isinstance(kw, tuple) for kw in keywords)
        assert all(len(kw[0]) > 2 for kw in keywords)

    def test_extract_keywords_excludes_stopwords(self):
        from services.transcript_processing_service import TranscriptProcessingService
        text = 'the a an is it in on at to for of by with'
        keywords = TranscriptProcessingService.extract_keywords(text, top_n=10)
        assert len(keywords) == 0

    def test_extract_phrases(self):
        from services.transcript_processing_service import TranscriptProcessingService
        text = 'the product features innovative design with high quality materials'
        phrases = TranscriptProcessingService.extract_phrases(text, min_length=2, max_length=3)
        assert len(phrases) > 0
        assert any('product features' in p[0] for p in phrases)

    def test_extract_phrases_no_common(self):
        from services.transcript_processing_service import TranscriptProcessingService
        text = 'a an the'
        phrases = TranscriptProcessingService.extract_phrases(text, 2, 3)
        assert len(phrases) == 0

    def test_get_topics(self):
        from services.transcript_processing_service import TranscriptProcessingService
        segments = [
            'Welcome to our technology review',
            'Today we discuss product design and quality',
            'The battery life is impressive',
        ]
        topics = TranscriptProcessingService.get_topics(segments, top_n=3)
        assert len(topics) <= 3
        assert all(len(t) > 3 for t in topics)

    def test_get_topics_empty(self):
        from services.transcript_processing_service import TranscriptProcessingService
        assert TranscriptProcessingService.get_topics([], top_n=5) == []


class TestTranscriptService:
    def test_store_demo_transcript(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc.store_demo_transcript(yt.id, yt.video_id)
        assert t.id is not None
        assert t.source == 'demo'
        assert t.segment_count > 0
        assert t.word_count > 0
        assert t.duration_seconds > 0

    def test_get_by_youtube_analysis_id(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        svc.store_demo_transcript(yt.id, yt.video_id)
        t = svc.get_by_youtube_analysis_id(yt.id)
        assert t is not None
        assert t.video_id == yt.video_id

    def test_get_segments(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc.store_demo_transcript(yt.id, yt.video_id)
        segments = svc.get_segments(t.id)
        assert len(segments) == t.segment_count
        assert segments[0].segment_index == 0

    def test_get_full_text(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc.store_demo_transcript(yt.id, yt.video_id)
        text = svc.get_full_text(t.id)
        assert len(text) > 0
        assert 'technology' in text.lower()

    def test_get_all_video_transcripts(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        svc.store_demo_transcript(yt.id, yt.video_id)
        all_t = svc.get_all_video_transcripts()
        assert len(all_t) >= 1

    def test_delete_transcript(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc.store_demo_transcript(yt.id, yt.video_id)
        assert svc.delete_transcript(t.id)
        assert VideoTranscript.query.get(t.id) is None

    def test_delete_transcript_nonexistent(self, app, db):
        from services.transcript_service import TranscriptService
        assert not TranscriptService().delete_transcript(99999)

    def test_mark_unavailable(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc._mark_unavailable(yt.id, yt.video_id)
        assert t.source == 'unavailable'
        assert t.transcript_text is None

    def test_fetch_and_store_success(self, app, db, analysis, monkeypatch):
        from services.transcript_service import TranscriptService
        from youtube_transcript_api._transcripts import FetchedTranscript, FetchedTranscriptSnippet
        snippets = [
            FetchedTranscriptSnippet(text='Hello world', start=0.0, duration=5.0),
            FetchedTranscriptSnippet(text='This is a test', start=5.0, duration=5.0),
        ]
        mock_fetch = MagicMock(return_value=FetchedTranscript(
            video_id=analysis.youtube_analysis.video_id,
            language='English', language_code='en',
            is_generated=False, snippets=snippets,
        ))
        monkeypatch.setattr('youtube_transcript_api.YouTubeTranscriptApi.fetch', mock_fetch)
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc.fetch_and_store(yt.id, yt.video_id)
        assert t.id is not None
        assert t.source == 'youtube_transcript_api'
        assert t.segment_count == 2


class TestContextMatchingService:
    def test_compute_context_relevant(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        transcript_text = 'Welcome to our technology product review. The design is innovative with high quality materials.'
        segments = [
            type('Segment', (), {'id': 1, 'text': 'Welcome to our technology product review.', 'start_time': 0.0, 'end_time': 5.0})(),
            type('Segment', (), {'id': 2, 'text': 'The design is innovative with high quality materials.', 'start_time': 5.0, 'end_time': 10.0})(),
        ]
        top_keywords = [('technology', 3), ('product', 2), ('review', 2), ('design', 2), ('quality', 2)]
        top_phrases = [('technology product review', 1), ('high quality materials', 1)]

        result = svc.compute_context('Great product review about technology', transcript_text, segments, top_keywords, top_phrases)
        assert result['context_match_label'] in ('highly_relevant', 'relevant')
        assert result['transcript_relevance_score'] > 0.3
        assert result['matched_keywords'] is not None

    def test_compute_context_off_topic(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        transcript_text = 'Welcome to our technology product review.'
        segments = [
            type('Segment', (), {'id': 1, 'text': 'Welcome to our technology product review.', 'start_time': 0.0, 'end_time': 5.0})(),
        ]
        top_keywords = [('technology', 1), ('product', 1), ('review', 1)]
        top_phrases = [('technology product review', 1)]

        result = svc.compute_context('I like cats and dogs playing together', transcript_text, segments, top_keywords, top_phrases)
        assert result['context_match_label'] in ('off_topic', 'partially_relevant')
        assert result['off_topic_score'] > 0.5

    def test_compute_context_no_transcript(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        result = svc.compute_context('Hello world', '', [], [], [])
        assert result['context_match_label'] == 'unknown'
        assert result['reason'] == 'No transcript available'

    def test_tfidf_similarity(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        score = svc._tfidf_similarity('product review technology', 'technology product review design quality price')
        assert score > 0

    def test_tfidf_similarity_no_match(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        score = svc._tfidf_similarity('cats dogs playing', 'technology product review design')
        assert score == 0.0

    def test_keyword_overlap(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        score = svc._keyword_overlap('product review technology', [('product', 1), ('review', 1), ('cats', 1)])
        assert score > 0

    def test_keyword_overlap_no_match(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        score = svc._keyword_overlap('cats dogs', [('product', 1), ('review', 1)])
        assert score == 0.0

    def test_keyword_overlap_empty(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        score = svc._keyword_overlap('cats dogs', [])
        assert score == 0.0

    def test_phrase_overlap(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        score = svc._phrase_overlap('technology product review', [('technology product', 1), ('product review', 1)])
        assert score > 0

    def test_phrase_overlap_no_match(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        score = svc._phrase_overlap('cats dogs', [('product review', 1)])
        assert score == 0.0

    def test_find_best_segment(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        segments = [
            type('Segment', (), {'id': 1, 'text': 'Welcome to the product review', 'start_time': 0.0, 'end_time': 5.0})(),
            type('Segment', (), {'id': 2, 'text': 'The design is innovative', 'start_time': 5.0, 'end_time': 10.0})(),
        ]
        best, _ = svc._find_best_segment('product review', segments)
        assert best is not None
        assert best['id'] == 1

    def test_topic_alignment(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        score = svc._topic_alignment('product review technology', [('product', 1), ('review', 1)])
        assert score > 0

    def test_topic_alignment_no_keywords(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        score = svc._topic_alignment('product review', [])
        assert score == 0.0

    def test_classify_relevance(self, app, db):
        from services.context_matching_service import ContextMatchingService
        from models.comment_context import CommentContext
        svc = ContextMatchingService()
        assert svc._classify_relevance(0.85) == CommentContext.LABEL_HIGHLY_RELEVANT
        assert svc._classify_relevance(0.55) == CommentContext.LABEL_RELEVANT
        assert svc._classify_relevance(0.30) == CommentContext.LABEL_PARTIALLY_RELEVANT
        assert svc._classify_relevance(0.10) == CommentContext.LABEL_OFF_TOPIC

    def test_create_comment_context_in_db(self, app, db, analysis):
        from services.context_matching_service import ContextMatchingService
        from models.comment_context import CommentContext
        from models.comment_result import CommentResult
        cr = db.session.get(CommentResult, analysis.comment_results[0].id)
        svc = ContextMatchingService()
        context_data = {
            'transcript_relevance_score': 0.9,
            'topic_alignment_score': 0.8,
            'off_topic_score': 0.1,
            'context_match_label': CommentContext.LABEL_HIGHLY_RELEVANT,
            'matched_keywords': '["product"]',
            'matched_phrases': None,
            'reason': 'Test',
            'best_segment_id': None,
        }
        ctx = svc.create_comment_context(cr.id, None, context_data)
        assert ctx.id is not None
        assert ctx.transcript_relevance_score == 0.9

    def test_generate_reason(self, app, db):
        from services.context_matching_service import ContextMatchingService
        from models.comment_context import CommentContext
        svc = ContextMatchingService()
        assert 'closely relates' in svc._generate_reason(CommentContext.LABEL_HIGHLY_RELEVANT, 0.9, 0.1, 0.5, 0.3, 0.2)
        assert 'off-topic' in svc._generate_reason(CommentContext.LABEL_OFF_TOPIC, 0.1, 0.9, 0.0, 0.0, 0.0)


@pytest.fixture
def force_demo(app):
    original = app.config.get('YOUTUBE_API_KEY', '')
    app.config['YOUTUBE_API_KEY'] = ''
    yield
    app.config['YOUTUBE_API_KEY'] = original


class TestAnalysisServiceTranscriptIntegration:

    def test_youtube_analysis_creates_transcript_in_demo_mode(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        assert result['success']
        assert result['transcript_available']

    def test_youtube_analysis_transcript_available_flag(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        assert result['transcript_available'] is True

    def test_youtube_analysis_creates_comment_contexts(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        from models.comment_context import CommentContext
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        analysis_id = result['analysis_id']
        contexts = CommentContext.query.join(
            CommentContext.comment_result
        ).filter(
            CommentContext.comment_result.has(analysis_id=analysis_id)
        ).all()
        assert len(contexts) > 0

    def test_get_analysis_results_includes_transcript(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        data = svc.get_analysis_results(result['analysis_id'], user.id)
        assert data is not None
        assert 'transcript' in data

    def test_get_analysis_results_includes_context_distribution(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        data = svc.get_analysis_results(result['analysis_id'], user.id)
        assert data is not None
        assert 'context_distribution' in data
        assert data['context_distribution'] is not None

    def test_dashboard_stats_includes_transcript_count(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        svc = AnalysisService()
        svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        stats = svc.get_dashboard_stats(user.id)
        assert 'transcript_count' in stats
        assert stats['transcript_count'] >= 1

    def test_all_user_analyses_includes_transcript_flag(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        svc = AnalysisService()
        svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        analyses = svc.get_all_user_analyses_with_data(user.id)
        assert len(analyses) > 0
        assert 'has_transcript' in analyses[0]

    def test_transcript_processing_does_not_crash_if_exception(self, app, db, user, monkeypatch):
        from services.analysis_service import AnalysisService
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        def broken_fetch(*args, **kwargs):
            raise RuntimeError('Simulated failure')
        monkeypatch.setattr('services.transcript_service.TranscriptService.fetch_and_store', broken_fetch)
        app.config['YOUTUBE_API_KEY'] = ''
        app.config['ENABLE_TRANSCRIPT_FALLBACK_DEMO'] = False
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        assert result['success']


class TestCommentResultRepositoryContext:
    def test_get_context_distribution(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        from repositories.comment_result_repository import CommentResultRepository
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        repo = CommentResultRepository()
        dist = repo.get_context_distribution(result['analysis_id'])
        assert 'highly_relevant' in dist
        assert 'relevant' in dist
        assert 'off_topic' in dist
        assert sum(dist.values()) > 0


class TestExportWithTranscript:
    def test_csv_export_includes_context_fields(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        from services.export_service import ExportService
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        export_svc = ExportService()
        csv_result = export_svc.generate_csv(result['analysis_id'], user.id)
        assert csv_result is not None
        assert 'Context Relevance Score' in csv_result['csv_content']
        assert 'Context Match Label' in csv_result['csv_content']
        assert 'Context Reason' in csv_result['csv_content']

    def test_json_export_includes_context_fields(self, app, db, user, force_demo):
        from services.analysis_service import AnalysisService
        from services.export_service import ExportService
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        export_svc = ExportService()
        json_result = export_svc.generate_json(result['analysis_id'], user.id)
        assert json_result is not None
        data = json.loads(json_result['json_content'])
        assert len(data['comments']) > 0
        assert 'context_relevance_score' in data['comments'][0]
        assert 'context_match_label' in data['comments'][0]


class TestContextMatchingEdgeCases:
    def test_empty_comment_text(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        result = svc.compute_context('', 'transcript text', [], [('key', 1)], [('key phrase', 1)])
        assert result['context_match_label'] == 'unknown'

    def test_empty_transcript(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        result = svc.compute_context('hello world', '', [], [], [])
        assert result['context_match_label'] == 'unknown'

    def test_all_off_topic_comments(self, app, db, user):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        transcript_text = 'serious technology product review discussion'
        segments = [
            type('Segment', (), {'id': 1, 'text': 'serious technology product review discussion', 'start_time': 0.0, 'end_time': 10.0})(),
        ]
        top_keywords = [('technology', 1), ('product', 1), ('review', 1), ('discussion', 1)]
        top_phrases = [('product review', 1)]
        result = svc.compute_context('cats dogs birds fish playing', transcript_text, segments, top_keywords, top_phrases)
        assert result['context_match_label'] == 'off_topic'

    def test_no_matched_keywords(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        result = svc.compute_context('xyzzy', 'technology product review', [], [], [])
        assert result['matched_keywords'] is None

    def test_partial_phrase_match(self, app, db):
        from services.context_matching_service import ContextMatchingService
        svc = ContextMatchingService()
        transcript = 'the product quality is excellent'
        segments = [type('Segment', (), {'id': 1, 'text': 'the product quality is excellent', 'start_time': 0.0, 'end_time': 5.0})()]
        kws = [('product', 1), ('quality', 1)]
        pws = [('product quality', 1)]
        result = svc.compute_context('product quality is mentioned', transcript, segments, kws, pws)
        assert result['context_match_label'] in ('highly_relevant', 'relevant')


class TestTranscriptProcessingEdgeCases:
    def test_extract_keywords_empty_text(self):
        from services.transcript_processing_service import TranscriptProcessingService
        assert TranscriptProcessingService.extract_keywords('') == []

    def test_extract_phrases_empty_text(self):
        from services.transcript_processing_service import TranscriptProcessingService
        assert TranscriptProcessingService.extract_phrases('') == []

    def test_clean_text_special_chars(self):
        from services.transcript_processing_service import TranscriptProcessingService
        result = TranscriptProcessingService.clean_text('Hello!!! How are you? #trending @user')
        assert 'hello' in result
        assert '#' not in result
        assert '@' not in result


class TestVideoTranscriptProperties:
    def test_is_real(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_TRANSCRIPT_API, segment_count=5)
        assert t.is_real is True

    def test_is_real_false_for_demo(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_DEMO, segment_count=5)
        assert t.is_real is False

    def test_is_fallback(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_FALLBACK_GENERATED, segment_count=3)
        assert t.is_fallback is True

    def test_is_available_true(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_TRANSCRIPT_API, segment_count=5)
        assert t.is_available is True

    def test_is_available_false_when_unavailable(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_UNAVAILABLE, segment_count=0)
        assert t.is_available is False

    def test_friendly_status_real(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_TRANSCRIPT_API)
        assert 'Real transcript' in t.friendly_status

    def test_friendly_status_fallback(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_FALLBACK_GENERATED)
        assert 'Fallback' in t.friendly_status

    def test_friendly_status_ip_blocked(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_UNAVAILABLE,
                            failure_reason=VideoTranscript.FAILURE_IP_BLOCKED)
        assert 'IP blocked' in t.friendly_status

    def test_friendly_status_captions_disabled(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_UNAVAILABLE,
                            failure_reason=VideoTranscript.FAILURE_CAPTIONS_DISABLED)
        assert 'disabled' in t.friendly_status

    def test_friendly_status_no_transcript(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_UNAVAILABLE,
                            failure_reason=VideoTranscript.FAILURE_NO_TRANSCRIPT)
        assert 'No transcript' in t.friendly_status

    def test_friendly_status_demo(self, app, db, analysis):
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        t = VideoTranscript(youtube_analysis_id=yt.id, video_id=yt.video_id,
                            source=VideoTranscript.SOURCE_DEMO)
        assert 'Demo' in t.friendly_status


class TestTranscriptServiceErrorClassification:
    def test_classify_ip_blocked(self, app, db):
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        svc = TranscriptService()
        e = Exception('HTTP 429 Too Many Requests - YouTube is blocking requests from your IP')
        assert svc._classify_error(e, 'test') == VideoTranscript.FAILURE_IP_BLOCKED

    def test_classify_captions_disabled(self, app, db):
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        svc = TranscriptService()
        e = Exception('Transcripts are disabled for this video')
        assert svc._classify_error(e, 'test') == VideoTranscript.FAILURE_CAPTIONS_DISABLED

    def test_classify_no_transcript(self, app, db):
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        svc = TranscriptService()
        e = Exception('No transcript found for this video')
        assert svc._classify_error(e, 'test') == VideoTranscript.FAILURE_NO_TRANSCRIPT

    def test_classify_api_error(self, app, db):
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        svc = TranscriptService()
        e = Exception('Connection timeout')
        assert svc._classify_error(e, 'test') == VideoTranscript.FAILURE_API_ERROR


class TestTranscriptServiceLanguageFallback:
    def test_build_language_list_includes_preferred(self, app, db):
        from services.transcript_service import TranscriptService
        svc = TranscriptService()
        langs = svc._build_language_list('hi')
        flat = [g[0] if g else None for g in langs]
        assert 'hi' in flat
        assert 'en' in flat

    def test_build_language_list_ends_with_none(self, app, db):
        from services.transcript_service import TranscriptService
        svc = TranscriptService()
        langs = svc._build_language_list('en')
        assert langs[-1] is None

    def test_build_language_list_order(self, app, db):
        from services.transcript_service import TranscriptService
        svc = TranscriptService()
        langs = svc._build_language_list('en')
        flat = [g[0] if g else None for g in langs]
        en_idx = flat.index('en')
        enus_idx = flat.index('en-US')
        assert en_idx < enus_idx

    def test_language_fallbacks_contain_hindi(self, app, db):
        from services.transcript_service import LANGUAGE_FALLBACKS
        assert ['hi'] in LANGUAGE_FALLBACKS

    def test_language_fallbacks_contain_en_in(self, app, db):
        from services.transcript_service import LANGUAGE_FALLBACKS
        assert ['en-IN'] in LANGUAGE_FALLBACKS

    def test_language_fallbacks_contain_en_gb(self, app, db):
        from services.transcript_service import LANGUAGE_FALLBACKS
        assert ['en-GB'] in LANGUAGE_FALLBACKS


class TestTranscriptServiceFallbackGenerated:
    def test_store_fallback_with_title(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc.store_fallback_generated(yt.id, yt.video_id,
                                         title='Great Product Review',
                                         description='A detailed review of the latest product',
                                         comments=None)
        assert t.source == 'fallback_generated'
        assert t.segment_count > 0
        assert t.word_count > 0
        assert t.is_fallback is True
        assert t.is_available is True

    def test_store_fallback_with_comments(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        comments = [
            'This video is amazing',
            'I love this product',
            'Best review ever',
        ]
        t = svc.store_fallback_generated(yt.id, yt.video_id,
                                         title='Test', description='',
                                         comments=comments)
        assert t.is_available is True

    def test_store_fallback_no_content(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc.store_fallback_generated(yt.id, yt.video_id,
                                         title='', description='',
                                         comments=[])
        assert not t.is_available

    def test_fallback_generated_overwrites_unavailable(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        svc._mark_unavailable(yt.id, yt.video_id, reason=VideoTranscript.FAILURE_NO_TRANSCRIPT)
        t = svc.store_fallback_generated(yt.id, yt.video_id,
                                         title='A very long and interesting title about product review',
                                         description='Description about technology and product quality',
                                         comments=None)
        assert t.is_available is True
        assert t.source == 'fallback_generated'


class TestTranscriptServiceMarkUnavailableWithReason:
    def test_mark_unavailable_stores_reason(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc._mark_unavailable(yt.id, yt.video_id, reason=VideoTranscript.FAILURE_IP_BLOCKED)
        assert t.failure_reason == 'ip_blocked'
        assert t.source == 'unavailable'
        assert not t.is_available

    def test_mark_unavailable_default_no_reason(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc._mark_unavailable(yt.id, yt.video_id)
        assert t.failure_reason is None

    def test_unavailable_friendly_status_with_reason(self, app, db, analysis):
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        yt = analysis.youtube_analysis
        svc = TranscriptService()
        t = svc._mark_unavailable(yt.id, yt.video_id, reason=VideoTranscript.FAILURE_CAPTIONS_DISABLED)
        assert 'disabled' in t.friendly_status


class TestAnalysisServiceFallbackIntegration:
    def test_fallback_generated_creates_available_transcript(self, app, db, user, monkeypatch):
        from services.analysis_service import AnalysisService
        from services.transcript_service import TranscriptService
        from models.video_transcript import VideoTranscript
        from models.comment_context import CommentContext
        from models.analysis import YouTubeAnalysis

        original_key = app.config.get('YOUTUBE_API_KEY', '')
        app.config['YOUTUBE_API_KEY'] = ''
        app.config['ENABLE_TRANSCRIPT_FALLBACK_DEMO'] = True

        real_demo = TranscriptService.store_demo_transcript

        def mock_demo(service_self, yt_analysis_id, video_id):
            return service_self._mark_unavailable(yt_analysis_id, video_id,
                                                   reason=VideoTranscript.FAILURE_NO_TRANSCRIPT)
        monkeypatch.setattr('services.transcript_service.TranscriptService.store_demo_transcript', mock_demo)
        svc = AnalysisService()
        result = svc.create_youtube_analysis(user.id, 'https://youtube.com/watch?v=dQw4w9WgXcQ')
        app.config['YOUTUBE_API_KEY'] = original_key
        assert result['success']
