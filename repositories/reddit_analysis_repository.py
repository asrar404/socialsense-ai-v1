from models.reddit_analysis import RedditAnalysis
from repositories.base import BaseRepository


class RedditAnalysisRepository(BaseRepository):
    def __init__(self):
        super().__init__(RedditAnalysis)

    def get_by_analysis_id(self, analysis_id):
        return self.model.query.filter_by(analysis_id=analysis_id).first()
