import csv
import io
import json
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
        yt = analysis.youtube_analysis

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['# Video Metadata'])
        writer.writerow(['Video ID', yt.video_id if yt else ''])
        writer.writerow(['Title', yt.video_title if yt else ''])
        writer.writerow(['Channel', yt.channel_name if yt else ''])
        writer.writerow(['Views', yt.view_count if yt else 0])
        writer.writerow(['Likes', yt.like_count if yt else 0])
        writer.writerow(['Comment Limit', yt.comment_limit if yt else 100])
        writer.writerow(['Demo Mode', 'Yes' if (yt and yt.is_demo) else 'No'])
        writer.writerow([])

        writer.writerow([
            'Comment',
            'Author',
            'Published At',
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
            published = c.published_at.strftime('%Y-%m-%d %H:%M:%S UTC') if c.published_at else ''
            writer.writerow([
                c.comment_text,
                c.author or '',
                published,
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

    def generate_json(self, analysis_id, user_id):
        analysis = self.analysis_repo.get_user_analysis_with_youtube(analysis_id, user_id)
        if not analysis:
            return None

        comments = self.comment_repo.get_by_analysis_id(analysis_id)
        yt = analysis.youtube_analysis

        video_metadata = {}
        if yt:
            video_metadata = {
                'video_id': yt.video_id,
                'title': yt.video_title,
                'description': yt.video_description,
                'channel': yt.channel_name,
                'published_at': yt.published_at.isoformat() if yt.published_at else None,
                'view_count': yt.view_count,
                'like_count': yt.like_count,
                'comment_limit': yt.comment_limit,
                'is_demo': yt.is_demo,
            }

        comments_data = []
        for c in comments:
            comments_data.append({
                'comment_text': c.comment_text,
                'author': c.author,
                'published_at': c.published_at.isoformat() if c.published_at else None,
                'spam_score': c.spam_score,
                'spam_explanation': c.spam_explanation,
                'toxicity_score': c.toxicity_score,
                'toxicity_explanation': c.toxicity_explanation,
                'sentiment': c.sentiment,
                'sentiment_score': c.sentiment_score,
                'sentiment_explanation': c.sentiment_explanation,
                'duplicate_score': c.duplicate_score,
                'duplicate_explanation': c.duplicate_explanation,
                'ai_like_score': c.ai_like_score,
                'ai_like_explanation': c.ai_like_explanation,
                'bot_score': c.bot_score,
                'bot_explanation': c.bot_explanation,
                'risk_score': c.risk_score,
                'risk_level': c.risk_level,
                'risk_explanation': c.risk_explanation,
            })

        data = {
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'analysis_id': analysis_id,
            'analysis_type': analysis.analysis_type,
            'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
            'video_metadata': video_metadata,
            'comment_count': len(comments_data),
            'comments': comments_data,
        }

        json_content = json.dumps(data, indent=2, default=str)

        filename = f"analysis_{analysis_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'reports'), filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_content)

        export_record = ReportExport(
            analysis_id=analysis_id,
            format_type='json',
            file_path=filepath,
        )
        db.session.add(export_record)
        db.session.commit()

        return {
            'json_content': json_content,
            'filename': filename,
            'filepath': filepath,
        }
