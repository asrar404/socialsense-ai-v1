def test_bot_human_like():
    from services.bot_detection_service import BotDetectionService
    result = BotDetectionService.analyze('I really enjoyed this video! The content was helpful and well presented.')
    assert result['bot_label'] == 'Low'
    assert result['bot_score'] <= 30


def test_bot_generic_phrasing():
    from services.bot_detection_service import BotDetectionService
    result = BotDetectionService.analyze('Great post. Thanks for sharing. Very informative. Keep it up.')
    assert result['bot_score'] > 0
    assert 'generic' in result['explanation'].lower()


def test_bot_template_structure():
    from services.bot_detection_service import BotDetectionService
    result = BotDetectionService.analyze('First of all, this content is excellent. It is important to note that this is well researched. The quality is outstanding.')
    assert result['bot_score'] >= 5
    assert result['explanation']


def test_bot_formal_language():
    from services.bot_detection_service import BotDetectionService
    result = BotDetectionService.analyze('Indeed, the aforementioned content is thus highly relevant.')
    assert result['bot_score'] > 0
    assert 'formal' in result['explanation'].lower()


def test_bot_confidence():
    from services.bot_detection_service import BotDetectionService
    result = BotDetectionService.analyze('Normal human comment here.')
    assert 0 <= result['confidence'] <= 1


def test_bot_disclaimer_present():
    from services.bot_detection_service import BotDetectionService
    result = BotDetectionService.analyze('Great video! Very informative.')
    assert 'probabilistic' in result['explanation']
    assert 'proof' in result['explanation']


def test_bot_empty():
    from services.bot_detection_service import BotDetectionService
    result = BotDetectionService.analyze('')
    assert result['bot_label'] == 'Low'
    assert result['bot_score'] == 0.0


def test_bot_repetitive():
    from services.bot_detection_service import BotDetectionService
    text = 'great great great great great video video video very very good good good'
    result = BotDetectionService.analyze(text)
    assert result['bot_score'] >= 0
    assert result['explanation']


def test_bot_similar_comments():
    from services.bot_detection_service import BotDetectionService
    all_texts = ['Great video! Very informative.', 'Great video! Very helpful.', 'Great video! Very educational.']
    result = BotDetectionService.analyze('Great video! Very informative.', all_texts)
    assert result['bot_score'] > 0
