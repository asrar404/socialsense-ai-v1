def test_toxicity_clean():
    from services.toxicity_service import ToxicityService
    result = ToxicityService.analyze('This is a very nice and friendly comment.')
    assert result['toxicity_label'] == 'Low'
    assert result['toxicity_score'] <= 15


def test_toxicity_profanity():
    from services.toxicity_service import ToxicityService
    result = ToxicityService.analyze('This is fucking terrible shit.')
    assert result['toxicity_score'] > 15
    assert 'Profanity' in result['explanation']


def test_toxicity_insults():
    from services.toxicity_service import ToxicityService
    result = ToxicityService.analyze('You are a stupid idiot moron.')
    assert result['toxicity_score'] > 15
    assert 'Insulting' in result['explanation']


def test_toxicity_threat():
    from services.toxicity_service import ToxicityService
    result = ToxicityService.analyze('I will kill you.')
    assert result['toxicity_score'] > 15
    assert 'Threatening' in result['explanation']


def test_toxicity_hate_speech():
    from services.toxicity_service import ToxicityService
    result = ToxicityService.analyze('This is racist and bigoted.')
    assert result['toxicity_score'] > 15


def test_toxicity_aggressive():
    from services.toxicity_service import ToxicityService
    result = ToxicityService.analyze('THIS IS ABSOLUTELY TERRIBLE!!!')
    assert result['toxicity_score'] > 0
    assert 'Aggressive' in result['explanation']


def test_toxicity_confidence():
    from services.toxicity_service import ToxicityService
    result = ToxicityService.analyze('This is fucking shit.')
    assert 0 <= result['confidence'] <= 1


def test_toxicity_empty():
    from services.toxicity_service import ToxicityService
    result = ToxicityService.analyze('')
    assert result['toxicity_label'] == 'Low'
    assert result['toxicity_score'] == 0.0
