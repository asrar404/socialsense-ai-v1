from datetime import datetime, timezone
from database import db


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class VideoTranscript(db.Model):
    __tablename__ = 'video_transcripts'

    SOURCE_YOUTUBE = 'youtube_captions'
    SOURCE_TRANSCRIPT_API = 'youtube_transcript_api'
    SOURCE_MANUAL = 'manual'
    SOURCE_DEMO = 'demo'
    SOURCE_FALLBACK_GENERATED = 'fallback_generated'
    SOURCE_UNAVAILABLE = 'unavailable'

    FAILURE_NONE = None
    FAILURE_IP_BLOCKED = 'ip_blocked'
    FAILURE_CAPTIONS_DISABLED = 'captions_disabled'
    FAILURE_NO_TRANSCRIPT = 'no_transcript_available'
    FAILURE_UNSUPPORTED_LANGUAGE = 'unsupported_language'
    FAILURE_API_ERROR = 'api_error'
    FAILURE_UNKNOWN = 'unknown'

    id = db.Column(db.Integer, primary_key=True)
    youtube_analysis_id = db.Column(db.Integer, db.ForeignKey('youtube_analyses.id'), nullable=False, index=True)
    video_id = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(10), nullable=True)
    transcript_text = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(30), nullable=False, default=SOURCE_UNAVAILABLE)
    is_auto_generated = db.Column(db.Boolean, default=False)
    segment_count = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    duration_seconds = db.Column(db.Float, nullable=True)
    summary = db.Column(db.Text, nullable=True)
    topics = db.Column(db.Text, nullable=True)
    failure_reason = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    youtube_analysis = db.relationship('YouTubeAnalysis', backref=db.backref('transcript', uselist=False, cascade='all, delete-orphan'))
    segments = db.relationship('TranscriptSegment', backref='transcript', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_real(self):
        return self.source in (self.SOURCE_YOUTUBE, self.SOURCE_TRANSCRIPT_API, self.SOURCE_MANUAL)

    @property
    def is_fallback(self):
        return self.source == self.SOURCE_FALLBACK_GENERATED

    @property
    def is_demo_transcript(self):
        return self.source == self.SOURCE_DEMO

    @property
    def is_available(self):
        return self.source != self.SOURCE_UNAVAILABLE and self.segment_count > 0

    @property
    def friendly_status(self):
        if self.is_real:
            return 'Real transcript'
        if self.is_fallback:
            return 'Fallback (generated)'
        if self.is_demo_transcript:
            return 'Demo transcript'
        if self.failure_reason:
            reasons = {
                self.FAILURE_IP_BLOCKED: 'YouTube blocked the request (IP blocked)',
                self.FAILURE_CAPTIONS_DISABLED: 'Captions are disabled for this video',
                self.FAILURE_NO_TRANSCRIPT: 'No transcript available for this video',
                self.FAILURE_UNSUPPORTED_LANGUAGE: 'Unsupported language',
                self.FAILURE_API_ERROR: 'Transcript API error',
            }
            return reasons.get(self.failure_reason, 'Transcript unavailable')
        return 'Transcript unavailable'

    def __repr__(self):
        return f'<VideoTranscript {self.video_id} ({self.source})>'
