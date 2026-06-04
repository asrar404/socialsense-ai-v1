def test_auth_service_register():
    from services.auth_service import AuthService
    from repositories.user_repository import UserRepository

    class MockUserRepo(UserRepository):
        def __init__(self):
            self.users = {}
            self.count = 0

        def username_exists(self, username):
            return username == 'taken'

        def email_exists(self, email):
            return email == 'taken@test.com'

        def create(self, **kwargs):
            self.count += 1
            obj = type('User', (), {'id': self.count, **kwargs})
            return obj

    service = AuthService(MockUserRepo())

    result = service.register('newuser', 'new@test.com', 'StrongPass1', 'StrongPass1')
    assert result['success'] is True

    result = service.register('ab', 'new@test.com', 'StrongPass1', 'StrongPass1')
    assert result['success'] is False
    assert 'username' in result['errors']

    result = service.register('taken', 'new@test.com', 'StrongPass1', 'StrongPass1')
    assert result['success'] is False
    assert 'username' in result['errors']


def test_youtube_service_extract():
    from services.youtube_service import YouTubeService

    assert YouTubeService.extract_video_id('dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('https://youtu.be/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('https://www.youtube.com/embed/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('https://www.youtube.com/v/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('https://www.youtube.com/shorts/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id('') is None
    assert YouTubeService.extract_video_id('invalid') is None


def test_youtube_service_extract_mixed_urls():
    from services.youtube_service import YouTubeService

    urls = [
        'http://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'youtube.com/watch?v=dQw4w9WgXcQ',
        'www.youtube.com/watch?v=dQw4w9WgXcQ',
    ]
    for url in urls:
        assert YouTubeService.extract_video_id(url) == 'dQw4w9WgXcQ', f'Failed for {url}'


def test_youtube_service_parse_datetime():
    from services.youtube_service import YouTubeService

    dt = YouTubeService._parse_youtube_datetime('2024-01-15T00:00:00Z')
    assert dt is not None
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 15

    assert YouTubeService._parse_youtube_datetime('') is None
    assert YouTubeService._parse_youtube_datetime(None) is None
    assert YouTubeService._parse_youtube_datetime('invalid') is None


def test_youtube_service_errors():
    from services.youtube_service import (
        YouTubeService, YouTubeAPIError, VideoNotFoundError,
        CommentsDisabledError, QuotaExceededError, InvalidVideoIdError
    )

    assert issubclass(VideoNotFoundError, YouTubeAPIError)
    assert issubclass(CommentsDisabledError, YouTubeAPIError)
    assert issubclass(QuotaExceededError, YouTubeAPIError)

    e = YouTubeAPIError('test')
    assert str(e) == 'test'
    assert e.error_type == 'api_error'

    e2 = VideoNotFoundError()
    assert e2.error_type == 'video_not_found'


def test_demo_service():
    from services.demo_service import DemoService
    demo = DemoService()

    info = demo.get_video_info()
    assert 'video_id' in info
    assert 'description' in info
    assert 'view_count' in info

    info = demo.get_video_info_by_id('test123')
    assert info['video_id'] == 'test123'
    assert info['is_demo'] is True

    comments = demo.get_comments()
    assert len(comments) > 10
    assert 'published_at' in comments[0]


def test_risk_scoring_service():
    from services.risk_scoring_service import RiskScoringService

    spam = RiskScoringService.calculate_spam_score('Buy now! Click here!')
    assert 0 <= spam['score'] <= 100
    assert spam['explanation']

    toxicity = RiskScoringService.calculate_toxicity_score('You are stupid!')
    assert 0 <= toxicity['score'] <= 100

    sentiment = RiskScoringService.calculate_sentiment('Great and amazing!')
    assert sentiment['label'] in ('Positive', 'Neutral', 'Negative')

    ai = RiskScoringService.calculate_ai_like_score('First of all, the content is excellent.')
    assert 0 <= ai['score'] <= 100

    bot = RiskScoringService.calculate_bot_score('spam spam spam', ['spam spam spam'])
    assert 0 <= bot['score'] <= 100

    risk = RiskScoringService.calculate_risk_score(80, 80, 10, 50, 60, 70)
    assert 0 <= risk['score'] <= 100
    assert risk['level'] in ('Low', 'Medium', 'High', 'Critical')
    assert risk['explanation']


def test_analysis_service_creates_full_metadata(app, db, user):
    from services.analysis_service import AnalysisService
    from flask import current_app
    service = AnalysisService()

    with app.app_context():
        current_app.config['YOUTUBE_API_KEY'] = ''
    result = service.create_youtube_analysis(user.id, 'dQw4w9WgXcQ', comment_limit=100)
    assert result['success'] is True
    assert result['is_demo'] is True
    assert result['comment_count'] > 0

    data = service.get_analysis_results(result['analysis_id'], user.id)
    assert data is not None
    assert data['youtube'].video_id == 'dQw4w9WgXcQ'
    assert data['youtube'].view_count > 0
    assert data['youtube'].comment_limit == 100
    assert data['comment_count'] > 0


def test_analysis_service_with_different_limits(app, db, user):
    from services.analysis_service import AnalysisService
    service = AnalysisService()

    for limit in (100, 500, 1000):
        result = service.create_youtube_analysis(user.id, 'dQw4w9WgXcQ', comment_limit=limit)
        assert result['success'] is True
        data = service.get_analysis_results(result['analysis_id'], user.id)
        assert data['youtube'].comment_limit == limit


def test_analysis_service_invalid_url(app, db, user):
    from services.analysis_service import AnalysisService
    service = AnalysisService()
    result = service.create_youtube_analysis(user.id, 'not-a-valid-url')
    assert result['success'] is False
    assert 'Invalid' in result['error']


def test_reddit_service_extract_post_id():
    from services.reddit_service import RedditService

    assert RedditService.extract_post_id('abc123def') == 'abc123def'
    assert RedditService.extract_post_id('https://www.reddit.com/r/technology/comments/abc123/') == 'abc123'
    assert RedditService.extract_post_id('https://redd.it/abc123') == 'abc123'
    assert RedditService.extract_post_id('') is None
    assert RedditService.extract_post_id('ab') is None


def test_reddit_service_extract_subreddit():
    from services.reddit_service import RedditService

    assert RedditService.extract_subreddit_name('technology') == 'technology'
    assert RedditService.extract_subreddit_name('https://www.reddit.com/r/technology/') == 'technology'
    assert RedditService.extract_subreddit_name('') is None


def test_reddit_demo_service():
    from services.reddit_service import RedditDemoService

    demo = RedditDemoService()

    info = demo.get_post_info('test123', 'AskReddit')
    assert info['post_id'] == 'test123'
    assert info['subreddit'] == 'AskReddit'
    assert info['is_demo'] is True

    comments = demo.get_comments()
    assert len(comments) > 10
    assert 'text' in comments[0]
    assert 'score' in comments[0]


def test_reddit_analysis_service_creates(app, db, user):
    from services.analysis_service import AnalysisService
    service = AnalysisService()

    result = service.create_reddit_analysis(user.id, 'abc123', subreddit='technology', comment_limit=100)
    assert result['success'] is True
    assert result['is_demo'] is True
    assert result['comment_count'] > 0

    data = service.get_analysis_results(result['analysis_id'], user.id)
    assert data is not None
    assert data['reddit'] is not None
    assert data['reddit'].post_id == 'abc123'
    assert data['reddit'].subreddit == 'technology'
    assert data['comment_count'] > 0


def test_reddit_analysis_with_different_limits(app, db, user):
    from services.analysis_service import AnalysisService
    service = AnalysisService()

    for limit in (100, 500, 1000):
        result = service.create_reddit_analysis(user.id, 'abc123', subreddit='test', comment_limit=limit)
        assert result['success'] is True
        data = service.get_analysis_results(result['analysis_id'], user.id)
        assert data['reddit'].comment_limit == limit
