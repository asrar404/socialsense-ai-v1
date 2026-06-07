from models.notification import Notification
from repositories.base import BaseRepository
from database import db


class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)

    def get_user_notifications(self, user_id, limit=50, unread_only=False):
        q = self.model.query.filter_by(user_id=user_id)
        if unread_only:
            q = q.filter_by(is_read=False)
        return q.order_by(Notification.created_at.desc()).limit(limit).all()

    def get_unread_count(self, user_id):
        return self.model.query.filter_by(user_id=user_id, is_read=False).count()

    def mark_as_read(self, notification_id, user_id):
        n = self.get_by_id(notification_id)
        if n and n.user_id == user_id:
            n.is_read = True
            db.session.commit()
            return n
        return None

    def mark_all_read(self, user_id):
        self.model.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()

    def create_notification(self, user_id, ntype, title, message=None, severity=Notification.SEVERITY_INFO, link_url=None):
        n = Notification(
            user_id=user_id, type=ntype, title=title,
            message=message, severity=severity, link_url=link_url,
        )
        db.session.add(n)
        db.session.commit()
        return n

    def delete_old_notifications(self, days=30):
        from datetime import datetime, timezone, timedelta
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
        old = self.model.query.filter(Notification.created_at < cutoff).all()
        for n in old:
            db.session.delete(n)
        db.session.commit()
        return len(old)
