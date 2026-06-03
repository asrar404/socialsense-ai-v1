from services.risk_scoring_service import RiskScoringService


def test_spam_score_high():
    result = RiskScoringService.calculate_spam_score(
        'BUY NOW!!! Click here http://spam.com Limited offer!!! subscribe please!!!'
    )
    assert result['score'] > 30
    assert 'promotional' in result['explanation'].lower() or 'link' in result['explanation'].lower()


def test_spam_score_low():
    result = RiskScoringService.calculate_spam_score('This is a nice video.')
    assert result['score'] <= 20


def test_toxicity_score_high():
    result = RiskScoringService.calculate_toxicity_score('You are stupid! This is the worst thing ever!')
    assert result['score'] > 20
    assert 'aggressive' in result['explanation'].lower()


def test_toxicity_score_low():
    result = RiskScoringService.calculate_toxicity_score('Great video, thanks for sharing!')
    assert result['score'] <= 10


def test_sentiment_positive():
    result = RiskScoringService.calculate_sentiment('This is absolutely amazing and wonderful!')
    assert result['label'] == 'Positive'
    assert result['score'] > 50


def test_sentiment_negative():
    result = RiskScoringService.calculate_sentiment('This is terrible and horrible. Worst video ever.')
    assert result['label'] == 'Negative'
    assert result['score'] < 50


def test_sentiment_neutral():
    result = RiskScoringService.calculate_sentiment('The video is okay.')
    assert result['label'] == 'Neutral'


def test_duplicate_score():
    comments = ['Hello world', 'Hello world', 'Different comment']
    result = RiskScoringService.calculate_duplicate_score('Hello world', comments)
    assert result['score'] > 0
    assert 'duplicate' in result['explanation'].lower()


def test_ai_like_score():
    result = RiskScoringService.calculate_ai_like_score(
        'First of all, the production quality is excellent. Furthermore, the content is well-researched. In conclusion, this is a great video.'
    )
    assert result['score'] > 0
    assert 'AI-generated' in result['explanation'] or 'Possible' in result['explanation']


def test_bot_score():
    comments = ['spam spam spam spam spam', 'spam spam spam spam spam']
    result = RiskScoringService.calculate_bot_score('spam spam spam spam spam', comments)
    assert result['score'] > 0


def test_risk_score_low():
    result = RiskScoringService.calculate_risk_score(5, 5, 75, 0, 5, 0)
    assert result['score'] <= 25
    assert result['level'] == 'Low'


def test_risk_score_high():
    result = RiskScoringService.calculate_risk_score(80, 90, 10, 50, 70, 60)
    assert result['score'] > 50
    assert result['level'] in ('High', 'Critical')


def test_risk_score_critical():
    result = RiskScoringService.calculate_risk_score(90, 95, 0, 80, 85, 80)
    assert result['score'] > 75
    assert result['level'] == 'Critical'
