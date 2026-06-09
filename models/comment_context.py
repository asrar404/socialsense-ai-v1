from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class CommentContext(db.Model):
    __tablename__ = 'comment_contexts'

    LABEL_HIGHLY_RELEVANT = 'highly_relevant'
    LABEL_RELEVANT = 'relevant'
    LABEL_PARTIALLY_RELEVANT = 'partially_relevant'
    LABEL_OFF_TOPIC = 'off_topic'
    LABEL_UNKNOWN = 'unknown'

    id = db.Column(db.Integer, primary_key=True)
    comment_result_id = db.Column(db.Integer, db.ForeignKey('comment_results.id'), nullable=False, unique=True, index=True)
    transcript_id = db.Column(db.Integer, db.ForeignKey('video_transcripts.id'), nullable=True)
    best_segment_id = db.Column(db.Integer, db.ForeignKey('transcript_segments.id'), nullable=True)
    transcript_relevance_score = db.Column(db.Float, default=0.0)
    topic_alignment_score = db.Column(db.Float, default=0.0)
    off_topic_score = db.Column(db.Float, default=0.0)
    context_match_label = db.Column(db.String(30), default=LABEL_UNKNOWN)
    matched_keywords = db.Column(db.Text, nullable=True)
    matched_phrases = db.Column(db.Text, nullable=True)
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    comment_result = db.relationship('CommentResult', backref=db.backref('context', uselist=False, cascade='all, delete-orphan'))
    best_segment = db.relationship('TranscriptSegment', backref='contexts', uselist=False)

    def __repr__(self):
        return f'<CommentContext {self.comment_result_id} ({self.context_match_label})>'
