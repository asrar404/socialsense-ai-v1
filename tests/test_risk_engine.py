def test_risk_low():
    from services.risk_engine import RiskEngine
    sentiment = {'score': 75.0, 'confidence': 0.8, 'label': 'Positive', 'explanation': ''}
    toxicity = {'toxicity_score': 0.0, 'confidence': 0.9, 'toxicity_label': 'Low', 'explanation': ''}
    spam = {'spam_score': 0.0, 'confidence': 0.9, 'spam_label': 'Low', 'explanation': ''}
    bot = {'bot_score': 0.0, 'confidence': 0.9, 'bot_label': 'Low', 'explanation': ''}
    result = RiskEngine.calculate(sentiment, toxicity, spam, bot)
    assert result['final_risk_label'] == 'Low'
    assert result['final_risk_score'] <= 15
    assert result['recommendation']


def test_risk_high():
    from services.risk_engine import RiskEngine
    sentiment = {'score': 10.0, 'confidence': 0.8, 'label': 'Negative', 'explanation': ''}
    toxicity = {'toxicity_score': 80.0, 'confidence': 0.9, 'toxicity_label': 'Critical', 'explanation': ''}
    spam = {'spam_score': 80.0, 'confidence': 0.9, 'spam_label': 'Critical', 'explanation': ''}
    bot = {'bot_score': 70.0, 'confidence': 0.9, 'bot_label': 'High', 'explanation': ''}
    result = RiskEngine.calculate(sentiment, toxicity, spam, bot)
    assert result['final_risk_label'] in ('High', 'Critical')
    assert result['final_risk_score'] >= 50


def test_risk_reasons():
    from services.risk_engine import RiskEngine
    sentiment = {'score': 10.0, 'confidence': 0.8, 'label': 'Negative', 'explanation': ''}
    toxicity = {'toxicity_score': 80.0, 'confidence': 0.9, 'toxicity_label': 'High', 'explanation': ''}
    spam = {'spam_score': 10.0, 'confidence': 0.9, 'spam_label': 'Low', 'explanation': ''}
    bot = {'bot_score': 10.0, 'confidence': 0.9, 'bot_label': 'Low', 'explanation': ''}
    result = RiskEngine.calculate(sentiment, toxicity, spam, bot)
    assert len(result['reasons']) >= 1
    assert 'Toxic' in result['reasons'][0] or 'Negative' in ' '.join(result['reasons'])


def test_risk_confidence():
    from services.risk_engine import RiskEngine
    sentiment = {'score': 50.0, 'confidence': 0.8, 'label': 'Neutral', 'explanation': ''}
    toxicity = {'toxicity_score': 0.0, 'confidence': 0.9, 'toxicity_label': 'Low', 'explanation': ''}
    spam = {'spam_score': 0.0, 'confidence': 0.9, 'spam_label': 'Low', 'explanation': ''}
    bot = {'bot_score': 0.0, 'confidence': 0.9, 'bot_label': 'Low', 'explanation': ''}
    result = RiskEngine.calculate(sentiment, toxicity, spam, bot)
    assert 0 <= result['confidence'] <= 1


def test_risk_with_duplicate():
    from services.risk_engine import RiskEngine
    sentiment = {'score': 50.0, 'confidence': 0.8, 'label': 'Neutral', 'explanation': ''}
    toxicity = {'toxicity_score': 0.0, 'confidence': 0.9, 'toxicity_label': 'Low', 'explanation': ''}
    spam = {'spam_score': 0.0, 'confidence': 0.9, 'spam_label': 'Low', 'explanation': ''}
    bot = {'bot_score': 0.0, 'confidence': 0.9, 'bot_label': 'Low', 'explanation': ''}
    result = RiskEngine.calculate(sentiment, toxicity, spam, bot, duplicate_score=80.0)
    assert result['reasons']
    assert 'Repeated' in result['reasons'][-1]


def test_risk_critical_label():
    from services.risk_engine import RiskEngine
    sentiment = {'score': 0.0, 'confidence': 0.9, 'label': 'Negative', 'explanation': ''}
    toxicity = {'toxicity_score': 95.0, 'confidence': 0.9, 'toxicity_label': 'Critical', 'explanation': ''}
    spam = {'spam_score': 90.0, 'confidence': 0.9, 'spam_label': 'Critical', 'explanation': ''}
    bot = {'bot_score': 90.0, 'confidence': 0.9, 'bot_label': 'Critical', 'explanation': ''}
    result = RiskEngine.calculate(sentiment, toxicity, spam, bot)
    assert result['final_risk_label'] == 'Critical'
    assert result['final_risk_score'] >= 70
