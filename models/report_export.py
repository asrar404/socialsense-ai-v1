from datetime import datetime, timezone
from database import db


class ReportExport(db.Model):
    __tablename__ = 'report_exports'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('analyses.id'), nullable=False, index=True)
    format_type = db.Column(db.String(20), nullable=False, default='csv')
    file_path = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f'<ReportExport {self.id} ({self.format_type})>'
