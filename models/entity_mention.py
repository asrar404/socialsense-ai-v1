from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class EntityMention(db.Model):
    __tablename__ = 'entity_mentions'

    MENTION_SOURCE_TITLE = 'title'
    MENTION_SOURCE_DESCRIPTION = 'description'
    MENTION_SOURCE_TRANSCRIPT = 'transcript'
    MENTION_SOURCE_COMMENT = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entities.id'), nullable=False, index=True)
    comment_result_id = db.Column(db.Integer, db.ForeignKey('comment_results.id'), nullable=True, index=True)
    transcript_segment_id = db.Column(db.Integer, db.ForeignKey('transcript_segments.id'), nullable=True, index=True)
    mention_text = db.Column(db.String(300), nullable=False)
    mention_source = db.Column(db.String(20), nullable=False, default=MENTION_SOURCE_COMMENT)
    context_snippet = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    comment_result = db.relationship('CommentResult', backref=db.backref('entity_mentions', lazy='dynamic', cascade='all, delete-orphan'))
    transcript_segment = db.relationship('TranscriptSegment', backref=db.backref('entity_mentions', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<EntityMention {self.mention_text} ({self.mention_source})>'
