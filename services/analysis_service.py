from flask import current_app
from database import db
from models.analysis import Analysis, YouTubeAnalysis
from models.reddit_analysis import RedditAnalysis
from models.comment_result import CommentResult
from repositories.analysis_repository import AnalysisRepository
from repositories.comment_result_repository import CommentResultRepository
from repositories.reddit_analysis_repository import RedditAnalysisRepository
from services.youtube_service import YouTubeService, YouTubeAPIError
from services.reddit_service import RedditService, RedditAPIError, RedditDemoService
from services.demo_service import DemoService
from services.risk_scoring_service import RiskScoringService


class AnalysisService:
    def __init__(self):
        self.analysis_repo = AnalysisRepository()
        self.comment_repo = CommentResultRepository()
        self.reddit_repo = RedditAnalysisRepository()
        self.youtube_service = YouTubeService()
        self.reddit_service = RedditService()
        self.reddit_demo = RedditDemoService()
        self.demo_service = DemoService()
        self.risk_scorer = RiskScoringService()

    def create_youtube_analysis(self, user_id, video_url, comment_limit=100):
        video_id = self.youtube_service.extract_video_id(video_url)
        if not video_id:
            return {'success': False, 'error': 'Invalid YouTube URL or Video ID.'}

        api_key = current_app.config.get('YOUTUBE_API_KEY', '')
        is_demo = not api_key

        video_info = None
        comments = []
        api_error = None

        if not is_demo:
            try:
                video_info = self.youtube_service.fetch_video_info(video_id)
                comments = self.youtube_service.fetch_comments(video_id, max_results=comment_limit)
            except YouTubeAPIError as e:
                api_error = e.error_type
                flash_message = str(e)
                return {'success': False, 'error': flash_message, 'api_error': e.error_type}
        else:
            video_info = self.demo_service.get_video_info_by_id(video_id)
            comments = self.demo_service.get_comments()

        if not video_info:
            video_info = {
                'video_id': video_id,
                'title': f'Video ({video_id})',
                'description': '',
                'channel': 'Unknown',
                'published_at': None,
                'view_count': 0,
                'like_count': 0,
                'comment_count': 0,
            }

        if not comments:
            comments = []

        analysis = self.analysis_repo.create(user_id=user_id, analysis_type='youtube')

        yt_analysis = YouTubeAnalysis(
            analysis_id=analysis.id,
            video_id=video_info['video_id'],
            video_title=video_info.get('title', 'Unknown Title'),
            video_description=video_info.get('description', ''),
            channel_name=video_info.get('channel', 'Unknown'),
            published_at=video_info.get('published_at'),
            view_count=video_info.get('view_count', 0),
            like_count=video_info.get('like_count', 0),
            comment_count=len(comments),
            comment_limit=comment_limit,
            is_demo=is_demo,
            api_error=api_error,
        )
        db.session.add(yt_analysis)
        db.session.commit()

        all_texts = [c['text'] for c in comments]
        for comment in comments:
            self._analyze_and_store_comment(analysis.id, comment, all_texts)

        return {
            'success': True,
            'analysis_id': analysis.id,
            'is_demo': is_demo,
            'comment_count': len(comments),
        }

    def create_reddit_analysis(self, user_id, post_id, subreddit=None, input_type='post', comment_limit=100):
        has_creds = bool(current_app.config.get('REDDIT_CLIENT_ID', '') and current_app.config.get('REDDIT_CLIENT_SECRET', ''))
        is_demo = not has_creds

        if not is_demo:
            try:
                post_info = self.reddit_service.fetch_post_info(post_id)
                comments = self.reddit_service.fetch_comments(post_id, max_results=comment_limit)
            except RedditAPIError as e:
                return {'success': False, 'error': str(e), 'api_error': e.error_type}
        else:
            post_info = self.reddit_demo.get_post_info(post_id, subreddit)
            comments = self.reddit_demo.get_comments()

        if not comments:
            comments = []

        analysis = self.analysis_repo.create(user_id=user_id, analysis_type='reddit')

        reddit = RedditAnalysis(
            analysis_id=analysis.id,
            post_id=post_info['post_id'],
            subreddit=post_info.get('subreddit', ''),
            post_title=post_info.get('title', 'Unknown Post'),
            post_body=post_info.get('body', ''),
            post_author=post_info.get('author', '[deleted]'),
            post_score=post_info.get('score', 0),
            upvote_ratio=post_info.get('upvote_ratio', 0.0),
            comment_count=len(comments),
            comment_limit=comment_limit,
            permalink=post_info.get('permalink', ''),
            created_utc=post_info.get('created_utc'),
            is_demo=is_demo,
        )
        db.session.add(reddit)
        db.session.commit()

        all_texts = [c['text'] for c in comments]
        for comment in comments:
            self._analyze_and_store_comment(analysis.id, comment, all_texts)

        return {
            'success': True,
            'analysis_id': analysis.id,
            'is_demo': is_demo,
            'comment_count': len(comments),
        }

    def _analyze_and_store_comment(self, analysis_id, comment, all_texts):
        text = comment['text']

        spam = self.risk_scorer.calculate_spam_score(text)
        toxicity = self.risk_scorer.calculate_toxicity_score(text)
        sentiment = self.risk_scorer.calculate_sentiment(text)
        duplicate = self.risk_scorer.calculate_duplicate_score(text, all_texts)
        ai_like = self.risk_scorer.calculate_ai_like_score(text)
        bot = self.risk_scorer.calculate_bot_score(text, all_texts)
        risk = self.risk_scorer.calculate_risk_score(
            spam['score'], toxicity['score'], sentiment['score'],
            duplicate['score'], ai_like['score'], bot['score']
        )

        result = CommentResult(
            analysis_id=analysis_id,
            comment_text=text,
            author=comment.get('author', 'Unknown'),
            published_at=comment.get('published_at'),
            spam_score=spam['score'],
            spam_explanation=spam['explanation'],
            toxicity_score=toxicity['score'],
            toxicity_explanation=toxicity['explanation'],
            sentiment=sentiment['label'],
            sentiment_score=sentiment['score'],
            sentiment_explanation=sentiment['explanation'],
            duplicate_score=duplicate['score'],
            duplicate_explanation=duplicate['explanation'],
            ai_like_score=ai_like['score'],
            ai_like_explanation=ai_like['explanation'],
            bot_score=bot['score'],
            bot_explanation=bot['explanation'],
            risk_score=risk['score'],
            risk_level=risk['level'],
            risk_explanation=risk['explanation'],
        )
        db.session.add(result)
        db.session.commit()

    def get_analysis_results(self, analysis_id, user_id):
        analysis = self.analysis_repo.get_user_analysis_with_reddit(analysis_id, user_id)
        if not analysis:
            return None

        comments = self.comment_repo.get_by_analysis_id(analysis_id)
        high_risk = self.comment_repo.get_high_risk_by_analysis(analysis_id)
        top_spam = self.comment_repo.get_top_spam_by_analysis(analysis_id, limit=5)
        top_toxic = self.comment_repo.get_top_toxic_by_analysis(analysis_id, limit=5)
        sentiment_dist = self.comment_repo.get_sentiment_distribution(analysis_id)
        risk_dist = self.comment_repo.get_risk_distribution(analysis_id)
        averages = self.comment_repo.get_average_scores_by_analysis(analysis_id)

        youtube = analysis.youtube_analysis
        reddit = analysis.reddit_analysis

        result = {
            'analysis': analysis,
            'comments': comments,
            'high_risk': high_risk,
            'top_spam': top_spam,
            'top_toxic': top_toxic,
            'sentiment_distribution': sentiment_dist,
            'risk_distribution': risk_dist,
            'averages': averages,
            'comment_count': len(comments),
        }

        if analysis.analysis_type == 'reddit' and reddit:
            result['reddit'] = reddit
            result['is_demo'] = reddit.is_demo
            result['api_error'] = reddit.api_error
            result['youtube'] = None
        elif youtube:
            result['youtube'] = youtube
            result['is_demo'] = youtube.is_demo
            result['api_error'] = youtube.api_error
            result['reddit'] = None
        else:
            return None

        return result

    def get_recent_user_analyses(self, user_id, limit=10):
        return self.analysis_repo.get_recent_by_user(user_id, limit)

    def get_dashboard_stats(self, user_id, platform='all'):
        analyses = self.analysis_repo.get_by_user_id(user_id)
        if platform != 'all':
            analyses = [a for a in analyses if a.analysis_type == platform]
        total_analyses = len(analyses)
        total_comments = 0
        total_spam = 0
        total_toxicity = 0
        total_sentiment = 0
        total_ai = 0
        total_risk = 0
        analysis_count = 0

        for analysis in analyses:
            averages = self.comment_repo.get_average_scores_by_analysis(analysis.id)
            comment_count = self.comment_repo.count_by_analysis(analysis.id)
            total_comments += comment_count
            if comment_count > 0:
                total_spam += averages['avg_spam']
                total_toxicity += averages['avg_toxicity']
                total_sentiment += averages['avg_sentiment']
                total_ai += averages['avg_ai_like']
                total_risk += averages['avg_risk']
                analysis_count += 1

        return {
            'total_analyses': total_analyses,
            'total_comments': total_comments,
            'avg_spam': round(total_spam / max(analysis_count, 1), 1),
            'avg_toxicity': round(total_toxicity / max(analysis_count, 1), 1),
            'avg_sentiment': round(total_sentiment / max(analysis_count, 1), 1),
            'avg_ai_like': round(total_ai / max(analysis_count, 1), 1),
            'avg_risk': round(total_risk / max(analysis_count, 1), 1),
        }

    def get_all_user_analyses_with_data(self, user_id, limit=None):
        analyses = self.analysis_repo.get_by_user_id(user_id)
        if limit:
            analyses = analyses[:limit]
        results = []
        for a in analyses:
            averages = self.comment_repo.get_average_scores_by_analysis(a.id)
            comment_count = self.comment_repo.count_by_analysis(a.id)
            yt = a.youtube_analysis
            reddit = a.reddit_analysis
            if a.analysis_type == 'reddit' and reddit:
                title = reddit.post_title or 'N/A'
                identifier = reddit.post_id
                is_demo = reddit.is_demo
                platform = 'reddit'
            elif yt:
                title = yt.video_title or 'N/A'
                identifier = yt.video_id
                is_demo = yt.is_demo
                platform = 'youtube'
            else:
                title = 'N/A'
                identifier = 'N/A'
                is_demo = False
                platform = 'unknown'
            results.append({
                'id': a.id,
                'title': title,
                'identifier': identifier,
                'platform': platform,
                'comment_count': comment_count,
                'avg_risk': averages['avg_risk'],
                'is_demo': is_demo,
                'created_at': a.created_at,
            })
        return results
