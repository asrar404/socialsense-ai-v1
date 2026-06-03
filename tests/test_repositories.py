def test_comment_repo_get_top_spam(app, db, analysis):
    from repositories.comment_result_repository import CommentResultRepository
    repo = CommentResultRepository()

    top_spam = repo.get_top_spam_by_analysis(analysis.id, limit=5)
    assert len(top_spam) >= 1
    assert top_spam[0].spam_score >= top_spam[-1].spam_score


def test_comment_repo_get_top_toxic(app, db, analysis):
    from repositories.comment_result_repository import CommentResultRepository
    repo = CommentResultRepository()

    top_toxic = repo.get_top_toxic_by_analysis(analysis.id, limit=5)
    assert len(top_toxic) >= 1


def test_comment_repo_count(app, db, analysis):
    from repositories.comment_result_repository import CommentResultRepository
    repo = CommentResultRepository()
    assert repo.count_by_analysis(analysis.id) == 2


def test_analysis_repo_count_by_user(app, db, user, analysis):
    from repositories.analysis_repository import AnalysisRepository
    repo = AnalysisRepository()
    assert repo.count_by_user(user.id) >= 1


def test_analysis_repo_recent(app, db, user, analysis):
    from repositories.analysis_repository import AnalysisRepository
    repo = AnalysisRepository()
    recent = repo.get_recent_by_user(user.id, limit=5)
    assert len(recent) >= 1


def test_user_repo_get_by_username(app, db, user):
    from repositories.user_repository import UserRepository
    repo = UserRepository()
    found = repo.get_by_username('testuser')
    assert found is not None
    assert found.email == 'test@example.com'

    not_found = repo.get_by_username('nonexistent')
    assert not_found is None


def test_user_repo_exists(app, db, user):
    from repositories.user_repository import UserRepository
    repo = UserRepository()
    assert repo.username_exists('testuser') is True
    assert repo.username_exists('nope') is False
    assert repo.email_exists('test@example.com') is True
    assert repo.email_exists('nope@test.com') is False
