from datetime import datetime, timezone
from database import db


class Analysis(db.Model):
    __tablename__ = 'analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    analysis_type = db.Column(db.String(50), nullable=False, default='youtube')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    youtube_analysis = db.relationship('YouTubeAnalysis', backref='analysis', uselist=False, cascade='all, delete-orphan')
    comment_results = db.relationship('CommentResult', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')
    report_exports = db.relationship('ReportExport', backref='analysis', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Analysis {self.id} ({self.analysis_type})>'


class YouTubeAnalysis(db.Model):
    __tablename__ = 'youtube_analyses'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False, unique=True, index=True)
    video_id = db.Column(db.String(20), nullable=False, index=True)
    video_title = db.Column(db.String(500), nullable=True)
    channel_name = db.Column(db.String(200), nullable=True)
    comment_count = db.Column(db.Integer, default=0)
    is_demo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f'<YouTubeAnalysis {self.video_id}>'
