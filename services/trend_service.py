from database import db
from models.analysis import Analysis
from models.comment_result import CommentResult
from datetime import datetime, timezone, timedelta
from sqlalchemy import func


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TrendService:
    def get_trends(self, user_id, days=30, platform=None):
        cutoff = _now() - timedelta(days=days)
        q = Analysis.query.filter(Analysis.user_id == user_id, Analysis.created_at >= cutoff)
        if platform and platform != 'all':
            q = q.filter(Analysis.analysis_type == platform)

        total = q.count()
        if total == 0:
            return self._empty_trends()

        avg_sentiment = db.session.query(func.avg(CommentResult.sentiment_score)).join(
            Analysis, CommentResult.analysis_id == Analysis.id
        ).filter(Analysis.user_id == user_id, CommentResult.created_at >= cutoff).scalar() or 0

        avg_toxicity = db.session.query(func.avg(CommentResult.toxicity_score)).join(
            Analysis, CommentResult.analysis_id == Analysis.id
        ).filter(Analysis.user_id == user_id, CommentResult.created_at >= cutoff).scalar() or 0

        avg_spam = db.session.query(func.avg(CommentResult.spam_score)).join(
            Analysis, CommentResult.analysis_id == Analysis.id
        ).filter(Analysis.user_id == user_id, CommentResult.created_at >= cutoff).scalar() or 0

        avg_bot = db.session.query(func.avg(CommentResult.bot_score)).join(
            Analysis, CommentResult.analysis_id == Analysis.id
        ).filter(Analysis.user_id == user_id, CommentResult.created_at >= cutoff).scalar() or 0

        avg_risk = db.session.query(func.avg(CommentResult.risk_score)).join(
            Analysis, CommentResult.analysis_id == Analysis.id
        ).filter(Analysis.user_id == user_id, CommentResult.created_at >= cutoff).scalar() or 0

        high_risk_count = db.session.query(func.count(CommentResult.id)).join(
            Analysis, CommentResult.analysis_id == Analysis.id
        ).filter(
            Analysis.user_id == user_id,
            CommentResult.created_at >= cutoff,
            CommentResult.risk_level.in_(['High', 'Critical']),
        ).scalar() or 0

        yt_count = Analysis.query.filter(
            Analysis.user_id == user_id, Analysis.created_at >= cutoff,
            Analysis.analysis_type == 'youtube',
        ).count()
        reddit_count = Analysis.query.filter(
            Analysis.user_id == user_id, Analysis.created_at >= cutoff,
            Analysis.analysis_type == 'reddit',
        ).count()

        return {
            'total_analyses': total,
            'avg_sentiment': round(avg_sentiment, 1),
            'avg_toxicity': round(avg_toxicity, 1),
            'avg_spam': round(avg_spam, 1),
            'avg_bot': round(avg_bot, 1),
            'avg_risk': round(avg_risk, 1),
            'high_risk_count': high_risk_count,
            'youtube_count': yt_count,
            'reddit_count': reddit_count,
        }

    def _empty_trends(self):
        return {
            'total_analyses': 0, 'avg_sentiment': 0, 'avg_toxicity': 0,
            'avg_spam': 0, 'avg_bot': 0, 'avg_risk': 0, 'high_risk_count': 0,
            'youtube_count': 0, 'reddit_count': 0,
        }
