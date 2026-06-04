def test_reddit_demo_service_get_subreddit_info():
    from services.reddit_service import RedditDemoService
    demo = RedditDemoService()
    info = demo.get_subreddit_info('technology')
    assert 'subreddit' in info
    assert 'subscribers' in info
    assert 'active_users' in info
    assert 'description' in info
    assert info['is_demo'] is True


def test_reddit_demo_service_get_post_info():
    from services.reddit_service import RedditDemoService
    demo = RedditDemoService()
    info = demo.get_post_info('test123', 'AskReddit')
    assert info['post_id'] == 'test123'
    assert info['subreddit'] == 'AskReddit'
    assert 'title' in info
    assert 'score' in info
    assert 'upvote_ratio' in info
    assert info['is_demo'] is True


def test_reddit_demo_service_get_comments():
    from services.reddit_service import RedditDemoService
    demo = RedditDemoService()
    comments = demo.get_comments()
    assert len(comments) > 0
    assert 'text' in comments[0]
    assert 'author' in comments[0]
    assert 'score' in comments[0]
    assert 'published_at' in comments[0]


def test_reddit_demo_analysis_stores_all_metadata(app, db, user, reddit_analysis):
    ra = reddit_analysis.reddit_analysis
    assert ra.post_body is not None
    assert ra.post_score > 0
    assert ra.upvote_ratio > 0
    assert ra.comment_limit == 100
    assert ra.subreddit == 'technology'
    assert ra.post_author == 'RedditUser'
    assert ra.permalink is not None


def test_reddit_demo_mode_via_demo_service(app, db, user):
    from services.demo_service import DemoService
    demo = DemoService()

    info = demo.get_reddit_subreddit_info('technology')
    assert info['is_demo'] is True

    info = demo.get_reddit_post_info('test123', 'AskReddit')
    assert info['post_id'] == 'test123'

    comments = demo.get_reddit_comments()
    assert len(comments) > 0
