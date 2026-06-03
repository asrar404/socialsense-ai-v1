from models.comment_result import CommentResult
from repositories.base import BaseRepository
from database import db


class CommentResultRepository(BaseRepository):
    def __init__(self):
        super().__init__(CommentResult)

    def get_by_analysis_id(self, analysis_id):
        return self.model.query.filter_by(analysis_id=analysis_id).all()

    def count_by_analysis(self, analysis_id):
        return self.model.query.filter_by(analysis_id=analysis_id).count()

    def get_high_risk_by_analysis(self, analysis_id, min_risk=50):
        return self.model.query.filter(
            CommentResult.analysis_id == analysis_id,
            CommentResult.risk_score >= min_risk
        ).order_by(CommentResult.risk_score.desc()).all()

    def get_sentiment_distribution(self, analysis_id):
        results = db.session.query(
            CommentResult.sentiment,
            db.func.count(CommentResult.id)
        ).filter(
            CommentResult.analysis_id == analysis_id
        ).group_by(CommentResult.sentiment).all()
        return {r[0] or 'Unknown': r[1] for r in results}

    def get_average_scores_by_analysis(self, analysis_id):
        from database import db
        result = db.session.query(
            db.func.avg(CommentResult.spam_score).label('avg_spam'),
            db.func.avg(CommentResult.toxicity_score).label('avg_toxicity'),
            db.func.avg(CommentResult.sentiment_score).label('avg_sentiment'),
            db.func.avg(CommentResult.ai_like_score).label('avg_ai_like'),
            db.func.avg(CommentResult.bot_score).label('avg_bot'),
            db.func.avg(CommentResult.risk_score).label('avg_risk')
        ).filter(CommentResult.analysis_id == analysis_id).first()
        return {
            'avg_spam': round(result.avg_spam or 0, 1),
            'avg_toxicity': round(result.avg_toxicity or 0, 1),
            'avg_sentiment': round(result.avg_sentiment or 0, 1),
            'avg_ai_like': round(result.avg_ai_like or 0, 1),
            'avg_bot': round(result.avg_bot or 0, 1),
            'avg_risk': round(result.avg_risk or 0, 1),
        }

    def get_risk_distribution(self, analysis_id):
        results = db.session.query(
            CommentResult.risk_level,
            db.func.count(CommentResult.id)
        ).filter(
            CommentResult.analysis_id == analysis_id
        ).group_by(CommentResult.risk_level).all()
        return {r[0]: r[1] for r in results}
