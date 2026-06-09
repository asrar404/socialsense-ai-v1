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
        analysis = self.analysis_repo.get_user_analysis_with_reddit(analysis_id, user_id)
        if not analysis:
            return None

        comments = self.comment_repo.get_by_analysis_id(analysis_id)
        yt = analysis.youtube_analysis
        reddit = analysis.reddit_analysis

        output = io.StringIO()
        writer = csv.writer(output)

        if analysis.analysis_type == 'reddit' and reddit:
            writer.writerow(['# Reddit Post Metadata'])
            writer.writerow(['Post ID', reddit.post_id])
            writer.writerow(['Subreddit', reddit.subreddit or ''])
            writer.writerow(['Title', reddit.post_title or ''])
            writer.writerow(['Author', reddit.post_author or ''])
            writer.writerow(['Score', reddit.post_score or 0])
            writer.writerow(['Upvote Ratio', reddit.upvote_ratio or 0.0])
            writer.writerow(['Comment Limit', reddit.comment_limit or 100])
            writer.writerow(['Demo Mode', 'Yes' if reddit.is_demo else 'No'])
        else:
            writer.writerow(['# Video Metadata'])
            writer.writerow(['Video ID', yt.video_id if yt else ''])
            writer.writerow(['Title', yt.video_title if yt else ''])
            writer.writerow(['Channel', yt.channel_name if yt else ''])
            writer.writerow(['Views', yt.view_count if yt else 0])
            writer.writerow(['Likes', yt.like_count if yt else 0])
            writer.writerow(['Comment Limit', yt.comment_limit if yt else 100])
            writer.writerow(['Demo Mode', 'Yes' if (yt and yt.is_demo) else 'No'])
        writer.writerow([])

        if analysis.analysis_summary:
            writer.writerow(['# Analysis Summary'])
            for line in analysis.analysis_summary.split('\n'):
                writer.writerow([line])
            writer.writerow([])

        writer.writerow([
            'Comment',
            'Author',
            'Published At',
            'Sentiment',
            'Sentiment Score',
            'Sentiment Confidence',
            'Sentiment Explanation',
            'Spam Score',
            'Spam Confidence',
            'Spam Explanation',
            'Toxicity Score',
            'Toxicity Confidence',
            'Toxicity Explanation',
            'Duplicate Score',
            'Duplicate Explanation',
            'Bot Score',
            'Bot Confidence',
            'Bot Explanation',
            'Risk Score',
            'Risk Level',
            'Risk Explanation',
            'Recommendation',
            'Context Relevance Score',
            'Context Match Label',
            'Context Reason',
        ])

        for c in comments:
            published = c.published_at.strftime('%Y-%m-%d %H:%M:%S UTC') if c.published_at else ''
            ctx = c.context
            writer.writerow([
                c.comment_text,
                c.author or '',
                published,
                c.sentiment or '',
                c.sentiment_score,
                c.sentiment_confidence or '',
                c.sentiment_explanation or '',
                c.spam_score,
                c.spam_confidence or '',
                c.spam_explanation or '',
                c.toxicity_score,
                c.toxicity_confidence or '',
                c.toxicity_explanation or '',
                c.duplicate_score,
                c.duplicate_explanation or '',
                c.bot_score,
                c.bot_confidence or '',
                c.bot_explanation or '',
                c.risk_score,
                c.risk_level,
                c.risk_explanation or '',
                c.recommendation or '',
                ctx.transcript_relevance_score if ctx else '',
                ctx.context_match_label.replace('_', ' ').title() if ctx else '',
                ctx.reason if ctx else '',
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
        analysis = self.analysis_repo.get_user_analysis_with_reddit(analysis_id, user_id)
        if not analysis:
            return None

        comments = self.comment_repo.get_by_analysis_id(analysis_id)
        yt = analysis.youtube_analysis
        reddit = analysis.reddit_analysis

        metadata = {}
        if analysis.analysis_type == 'reddit' and reddit:
            metadata = {
                'platform': 'reddit',
                'post_id': reddit.post_id,
                'subreddit': reddit.subreddit,
                'title': reddit.post_title,
                'body': reddit.post_body,
                'author': reddit.post_author,
                'score': reddit.post_score,
                'upvote_ratio': reddit.upvote_ratio,
                'comment_limit': reddit.comment_limit,
                'permalink': reddit.permalink,
                'created_utc': reddit.created_utc.isoformat() if reddit.created_utc else None,
                'is_demo': reddit.is_demo,
            }
        elif yt:
            metadata = {
                'platform': 'youtube',
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
            ctx = c.context
            comments_data.append({
                'comment_text': c.comment_text,
                'author': c.author,
                'published_at': c.published_at.isoformat() if c.published_at else None,
                'sentiment': c.sentiment,
                'sentiment_score': c.sentiment_score,
                'sentiment_confidence': c.sentiment_confidence,
                'sentiment_explanation': c.sentiment_explanation,
                'spam_score': c.spam_score,
                'spam_confidence': c.spam_confidence,
                'spam_explanation': c.spam_explanation,
                'toxicity_score': c.toxicity_score,
                'toxicity_confidence': c.toxicity_confidence,
                'toxicity_explanation': c.toxicity_explanation,
                'duplicate_score': c.duplicate_score,
                'duplicate_explanation': c.duplicate_explanation,
                'ai_like_score': c.ai_like_score,
                'ai_like_explanation': c.ai_like_explanation,
                'bot_score': c.bot_score,
                'bot_confidence': c.bot_confidence,
                'bot_explanation': c.bot_explanation,
                'risk_score': c.risk_score,
                'risk_level': c.risk_level,
                'risk_explanation': c.risk_explanation,
                'recommendation': c.recommendation,
                'context_relevance_score': ctx.transcript_relevance_score if ctx else None,
                'context_match_label': ctx.context_match_label.replace('_', ' ').title() if ctx else None,
                'context_reason': ctx.reason if ctx else None,
            })

        data = {
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'analysis_id': analysis_id,
            'analysis_type': analysis.analysis_type,
            'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
            'metadata': metadata,
            'analysis_summary': analysis.analysis_summary,
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
