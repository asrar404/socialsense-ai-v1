import csv
import io
import os
from datetime import datetime, timezone
from flask import current_app
from database import db
from models.report_export import ReportExport
from repositories.comment_result_repository import CommentResultRepository
from repositories.analysis_repository import AnalysisRepository
from repositories.report_export_repository import ReportExportRepository


class ExportService:
    def __init__(self):
        self.comment_repo = CommentResultRepository()
        self.analysis_repo = AnalysisRepository()
        self.export_repo = ReportExportRepository()

    def generate_csv(self, analysis_id, user_id):
        analysis = self.analysis_repo.get_user_analysis_with_youtube(analysis_id, user_id)
        if not analysis:
            return None

        comments = self.comment_repo.get_by_analysis_id(analysis_id)

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            'Comment',
            'Author',
            'Spam Score',
            'Spam Explanation',
            'Toxicity Score',
            'Toxicity Explanation',
            'Sentiment',
            'Sentiment Score',
            'Sentiment Explanation',
            'Duplicate Score',
            'Duplicate Explanation',
            'AI-like Score',
            'AI-like Explanation',
            'Bot Score',
            'Bot Explanation',
            'Risk Score',
            'Risk Level',
            'Risk Explanation',
        ])

        for c in comments:
            writer.writerow([
                c.comment_text,
                c.author or '',
                c.spam_score,
                c.spam_explanation or '',
                c.toxicity_score,
                c.toxicity_explanation or '',
                c.sentiment or '',
                c.sentiment_score,
                c.sentiment_explanation or '',
                c.duplicate_score,
                c.duplicate_explanation or '',
                c.ai_like_score,
                c.ai_like_explanation or '',
                c.bot_score,
                c.bot_explanation or '',
                c.risk_score,
                c.risk_level,
                c.risk_explanation or '',
            ])

        csv_content = output.getvalue()
        output.close()

        filename = f"analysis_{analysis_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'reports'), filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            f.write(csv_content)

        export_record = ReportExport(
            analysis_id=analysis_id,
            format_type='csv',
            file_path=filepath,
        )
        db.session.add(export_record)
        db.session.commit()

        return {
            'csv_content': csv_content,
            'filename': filename,
            'filepath': filepath,
        }
