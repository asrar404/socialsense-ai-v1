from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class EntityContext(db.Model):
    __tablename__ = 'entity_contexts'

    LABEL_HIGHLY_RELATED = 'highly_related'
    LABEL_RELATED = 'related'
    LABEL_PARTIALLY_RELATED = 'partially_related'
    LABEL_UNRELATED = 'unrelated'
    LABEL_UNKNOWN = 'unknown'

    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False, index=True)
    comment_result_id = db.Column(db.Integer, db.ForeignKey('comment_results.id'), nullable=False, index=True)
    entity_sentiment = db.Column(db.String(20), nullable=True)
    entity_sentiment_score = db.Column(db.Float, default=0.0)
    entity_risk_score = db.Column(db.Float, default=0.0)
    entity_relevance_score = db.Column(db.Float, default=0.0)
    entity_context_label = db.Column(db.String(30), default=LABEL_UNKNOWN)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    comment_result = db.relationship('CommentResult', backref=db.backref('entity_contexts', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<EntityContext entity={self.entity_id} sentiment={self.entity_sentiment}>'
