def test_reddit_service_extract_post_id():
    from services.reddit_service import RedditService

    assert RedditService.extract_post_id('abc123def') == 'abc123def'
    assert RedditService.extract_post_id('https://www.reddit.com/r/technology/comments/abc123/') == 'abc123'
    assert RedditService.extract_post_id('https://www.reddit.com/r/technology/comments/abc123/xyz/') == 'abc123'
    assert RedditService.extract_post_id('https://redd.it/abc123') == 'abc123'
    assert RedditService.extract_post_id('https://old.reddit.com/r/AskReddit/comments/def456/') == 'def456'
    assert RedditService.extract_post_id('') is None
    assert RedditService.extract_post_id('ab') is None


def test_reddit_service_extract_subreddit():
    from services.reddit_service import RedditService

    assert RedditService.extract_subreddit_name('technology') == 'technology'
    assert RedditService.extract_subreddit_name('AskReddit') == 'askreddit'
    assert RedditService.extract_subreddit_name('https://www.reddit.com/r/technology/') == 'technology'
    assert RedditService.extract_subreddit_name('https://www.reddit.com/r/AskReddit/comments/abc123/') == 'askreddit'
    assert RedditService.extract_subreddit_name('https://old.reddit.com/r/python') == 'python'
    assert RedditService.extract_subreddit_name('') is None
    assert RedditService.extract_subreddit_name('a') is None


def test_reddit_service_extract_post_info():
    from services.reddit_service import RedditService

    info = RedditService.extract_post_info('abc123def')
    assert info is not None
    assert info['post_id'] == 'abc123def'
    assert info['subreddit'] is None

    info = RedditService.extract_post_info('https://www.reddit.com/r/technology/comments/abc123/')
    assert info is not None
    assert info['post_id'] == 'abc123'
    assert info['subreddit'] == 'technology'

    info = RedditService.extract_post_info('')
    assert info is None

    info = RedditService.extract_post_info('ab')
    assert info is None


def test_reddit_service_error_classes():
    from services.reddit_service import (
        RedditAPIError, InvalidSubredditError, PostNotFoundError,
        PrivateSubredditError, RedditRateLimitError, MissingCredentialsError
    )

    assert issubclass(InvalidSubredditError, RedditAPIError)
    assert issubclass(PostNotFoundError, RedditAPIError)
    assert issubclass(PrivateSubredditError, RedditAPIError)
    assert issubclass(RedditRateLimitError, RedditAPIError)
    assert issubclass(MissingCredentialsError, RedditAPIError)

    e = RedditAPIError('test')
    assert str(e) == 'test'
    assert e.error_type == 'reddit_api_error'

    e2 = InvalidSubredditError()
    assert e2.error_type == 'invalid_subreddit'

    e3 = MissingCredentialsError()
    assert 'credentials' in str(e3).lower()


def test_reddit_demo_service_basics():
    from services.reddit_service import RedditDemoService

    demo = RedditDemoService()

    info = demo.get_subreddit_info('technology')
    assert info['subreddit'] == 'technology'
    assert info['subscribers'] > 0
    assert info['is_demo'] is True

    info = demo.get_post_info('test456', 'AskReddit')
    assert info['post_id'] == 'test456'
    assert info['subreddit'] == 'AskReddit'
    assert info['is_demo'] is True

    comments = demo.get_comments()
    assert len(comments) > 0
    assert 'text' in comments[0]
    assert 'score' in comments[0]
    assert 'author' in comments[0]
