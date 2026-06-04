from models.analysis import Analysis
from repositories.base import BaseRepository


class AnalysisRepository(BaseRepository):
    def __init__(self):
        super().__init__(Analysis)

    def get_by_user_id(self, user_id):
        return self.model.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).all()

    def get_user_analysis_with_youtube(self, analysis_id, user_id):
        return self.model.query.filter_by(id=analysis_id, user_id=user_id).first()

    def get_user_analysis_with_reddit(self, analysis_id, user_id):
        return self.model.query.filter_by(id=analysis_id, user_id=user_id).first()

    def count_by_user(self, user_id):
        return self.model.query.filter_by(user_id=user_id).count()

    def get_recent_by_user(self, user_id, limit=10):
        return self.model.query.filter_by(user_id=user_id).order_by(
            Analysis.created_at.desc()).limit(limit).all()
