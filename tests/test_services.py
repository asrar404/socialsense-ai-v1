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


def test_demo_service():
    from services.demo_service import DemoService
    demo = DemoService()

    info = demo.get_video_info()
    assert 'video_id' in info

    info = demo.get_video_info_by_id('test123')
    assert info['video_id'] == 'test123'

    comments = demo.get_comments()
    assert len(comments) > 10


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
