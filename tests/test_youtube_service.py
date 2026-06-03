import pytest


def test_fetch_video_info_no_api_key(app):
    from services.youtube_service import YouTubeService, YouTubeAPIError
    with app.app_context():
        app.config['YOUTUBE_API_KEY'] = ''
        service = YouTubeService()
        with pytest.raises(YouTubeAPIError) as exc:
            service.fetch_video_info('dQw4w9WgXcQ')
        assert 'API key' in str(exc.value)


def test_fetch_comments_no_api_key(app):
    from services.youtube_service import YouTubeService, YouTubeAPIError
    with app.app_context():
        app.config['YOUTUBE_API_KEY'] = ''
        service = YouTubeService()
        with pytest.raises(YouTubeAPIError) as exc:
            service.fetch_comments('dQw4w9WgXcQ')
        assert 'API key' in str(exc.value)


def test_youtube_api_error_hierarchy():
    from services.youtube_service import (
        YouTubeAPIError, VideoNotFoundError, CommentsDisabledError,
        QuotaExceededError, NetworkError, InvalidVideoIdError, PrivateVideoError
    )

    for exc_class in [VideoNotFoundError, CommentsDisabledError,
                      QuotaExceededError, NetworkError, InvalidVideoIdError,
                      PrivateVideoError]:
        assert issubclass(exc_class, YouTubeAPIError), f'{exc_class} is not a subclass'


def test_youtube_api_error_types():
    from services.youtube_service import (
        VideoNotFoundError, CommentsDisabledError, QuotaExceededError,
        NetworkError, InvalidVideoIdError, PrivateVideoError
    )

    assert VideoNotFoundError().error_type == 'video_not_found'
    assert CommentsDisabledError().error_type == 'comments_disabled'
    assert QuotaExceededError().error_type == 'quota_exceeded'
    assert NetworkError().error_type == 'network_error'
    assert InvalidVideoIdError().error_type == 'invalid_video_id'
    assert PrivateVideoError().error_type == 'private_video'


def test_youtube_service_extract_with_special_chars():
    from services.youtube_service import YouTubeService

    valid_ids = [
        'dQw4w9WgXcQ',
        'jNQXAC9IVRw',
            'a-b_c1D2eF3',
    ]
    for vid in valid_ids:
        assert YouTubeService.extract_video_id(vid) == vid, f'Failed for {vid}'

    invalid_ids = [
        'abc',
        'abcdefghijklm',
        'abc defghijk',
        '',
        None,
    ]
    for vid in invalid_ids:
        if vid is not None:
            assert YouTubeService.extract_video_id(vid) is None, f'Should be None for {vid}'


def test_youtube_service_extract_from_playlist():
    from services.youtube_service import YouTubeService

    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf'
    assert YouTubeService.extract_video_id(url) == 'dQw4w9WgXcQ'

    url2 = 'https://www.youtube.com/watch?v=jNQXAC9IVRw&index=2'
    assert YouTubeService.extract_video_id(url2) == 'jNQXAC9IVRw'


def test_youtube_service_extract_with_timestamp():
    from services.youtube_service import YouTubeService

    url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120s'
    assert YouTubeService.extract_video_id(url) == 'dQw4w9WgXcQ'


def test_youtube_service_extract_mobile_url():
    from services.youtube_service import YouTubeService

    url = 'https://m.youtube.com/watch?v=dQw4w9WgXcQ'
    assert YouTubeService.extract_video_id(url) == 'dQw4w9WgXcQ'
