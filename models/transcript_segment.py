from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TranscriptSegment(db.Model):
    __tablename__ = 'transcript_segments'

    id = db.Column(db.Integer, primary_key=True)
    transcript_id = db.Column(db.Integer, db.ForeignKey('video_transcripts.id'), nullable=False, index=True)
    start_time = db.Column(db.Float, nullable=False)
    end_time = db.Column(db.Float, nullable=False)
    text = db.Column(db.Text, nullable=False)
    word_count = db.Column(db.Integer, default=0)
    segment_index = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    def __repr__(self):
        return f'<TranscriptSegment {self.segment_index} ({self.start_time}s-{self.end_time}s)>'
