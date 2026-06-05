def test_sentiment_positive():
    from services.sentiment_service import SentimentService
    result = SentimentService.analyze('This is absolutely amazing and wonderful!')
    assert result['label'] == 'Positive'
    assert result['score'] >= 65
    assert 0 <= result['confidence'] <= 1
    assert result['explanation']


def test_sentiment_negative():
    from services.sentiment_service import SentimentService
    result = SentimentService.analyze('This is terrible and horrible garbage.')
    assert result['label'] == 'Negative'
    assert result['score'] <= 35
    assert result['confidence'] > 0


def test_sentiment_neutral():
    from services.sentiment_service import SentimentService
    result = SentimentService.analyze('The sky is blue and grass is green.')
    assert result['label'] == 'Neutral'
    assert 35 < result['score'] < 65


def test_sentiment_empty():
    from services.sentiment_service import SentimentService
    result = SentimentService.analyze('')
    assert result['label'] == 'Neutral'
    assert result['score'] == 0.0


def test_sentiment_strongly_positive():
    from services.sentiment_service import SentimentService
    result = SentimentService.analyze('Absolutely incredible! The best thing ever! Brilliant!')
    assert result['label'] == 'Positive'
    assert result['score'] >= 65
    assert 'strongly' in result['explanation'].lower()


def test_sentiment_strongly_negative():
    from services.sentiment_service import SentimentService
    result = SentimentService.analyze('Absolutely terrible. The worst garbage ever. Horrible.')
    assert result['label'] == 'Negative'
    assert result['score'] <= 35
    assert 'strongly' in result['explanation'].lower() or 'criticism' in result['explanation'].lower()


def test_sentiment_confidence_high():
    from services.sentiment_service import SentimentService
    result = SentimentService.analyze('This is good and great and wonderful and amazing!')
    assert result['confidence'] > 0.5


def test_sentiment_confidence_low():
    from services.sentiment_service import SentimentService
    result = SentimentService.analyze('Hello world.')
    assert result['confidence'] <= 0.5
