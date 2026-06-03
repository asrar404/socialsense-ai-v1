from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username):
        return self.model.query.filter_by(username=username).first()

    def get_by_email(self, email):
        return self.model.query.filter_by(email=email).first()

    def username_exists(self, username):
        return self.model.query.filter_by(username=username).count() > 0

    def email_exists(self, email):
        return self.model.query.filter_by(email=email).count() > 0

    def get_recent_analyses(self, user_id, limit=5):
        from models.analysis import Analysis
        return Analysis.query.filter_by(user_id=user_id).order_by(Analysis.created_at.desc()).limit(limit).all()
