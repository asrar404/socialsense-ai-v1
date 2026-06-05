def test_spam_clean():
    from services.spam_service import SpamService
    result = SpamService.analyze('This is a normal friendly comment about the topic.')
    assert result['spam_label'] == 'Low'
    assert result['spam_score'] <= 15


def test_spam_promotional():
    from services.spam_service import SpamService
    result = SpamService.analyze('Buy now! Click here! Limited offer! Check out this link!')
    assert result['spam_score'] > 15
    assert 'promotional' in result['explanation'].lower()


def test_spam_links():
    from services.spam_service import SpamService
    result = SpamService.analyze('Visit https://spam.example.com and click here')
    assert result['spam_score'] > 15
    assert 'links' in result['explanation'].lower()


def test_spam_excessive_caps():
    from services.spam_service import SpamService
    result = SpamService.analyze('BUY NOW THIS IS LIMITED OFFER ACT NOW')
    assert result['spam_score'] > 0
    assert 'capitalization' in result['explanation'].lower()


def test_spam_excessive_emojis():
    from services.spam_service import SpamService
    result = SpamService.analyze('Check this out 😀😀😀😀😀😀😀😀')
    assert result['spam_score'] > 0
    assert 'emoji' in result['explanation'].lower()


def test_spam_scam_language():
    from services.spam_service import SpamService
    result = SpamService.analyze('Congratulations! You won the lottery! Send money now!')
    assert result['spam_score'] > 15
    assert 'Scam' in result['explanation'] or 'scam' in result['explanation'].lower()


def test_spam_duplicate_content():
    from services.spam_service import SpamService
    all_texts = ['Great video!', 'Great video!', 'Great video!']
    result = SpamService.analyze('Great video!', all_texts)
    assert result['spam_score'] >= 10


def test_spam_label_critical():
    from services.spam_service import SpamService
    result = SpamService.analyze('BUY NOW!!! https://spam.com LIMITED OFFER!!! CLICK HERE!!! FREE MONEY!!!')
    assert result['spam_label'] in ('High', 'Critical')


def test_spam_confidence():
    from services.spam_service import SpamService
    result = SpamService.analyze('Normal comment.')
    assert 0 <= result['confidence'] <= 1


def test_spam_empty():
    from services.spam_service import SpamService
    result = SpamService.analyze('')
    assert result['spam_label'] == 'Low'
    assert result['spam_score'] == 0.0
