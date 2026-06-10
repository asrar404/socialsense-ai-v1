import json
from flask import current_app
from database import db
from models.video_context_history import VideoContextHistory
from models.entity_history import EntityHistory


class VideoHistoryService:
    def record_video_analysis(self, analysis_id, user_id, video_id, channel_id,
                              video_title, entity_count, avg_sentiment, avg_risk,
                              top_entities=None):
        existing = VideoContextHistory.query.filter_by(analysis_id=analysis_id).first()
        if existing:
            return existing

        history = VideoContextHistory(
            analysis_id=analysis_id,
            user_id=user_id,
            video_id=video_id,
            channel_id=channel_id,
            video_title=video_title,
            entity_count=entity_count,
            avg_sentiment=round(avg_sentiment, 1),
            avg_risk=round(avg_risk, 1),
            top_entities=json.dumps(top_entities) if top_entities else None,
        )
        db.session.add(history)
        db.session.commit()
        return history

    def get_previous_videos(self, channel_id, user_id, exclude_analysis_id=None, limit=10):
        query = VideoContextHistory.query.filter_by(
            channel_id=channel_id, user_id=user_id
        ).order_by(VideoContextHistory.processed_at.desc())
        if exclude_analysis_id:
            query = query.filter(VideoContextHistory.analysis_id != exclude_analysis_id)
        return query.limit(limit).all()

    def find_recurring_entities(self, channel_id, user_id, exclude_analysis_id=None):
        histories = self.get_previous_videos(channel_id, user_id, exclude_analysis_id, limit=50)
        entity_names = set()
        for h in histories:
            if h.top_entities:
                try:
                    names = json.loads(h.top_entities)
                    entity_names.update(names)
                except (json.JSONDecodeError, TypeError):
                    pass
        return list(entity_names)

    def get_trend_statistics(self, channel_id, user_id, exclude_analysis_id=None, limit=20):
        histories = self.get_previous_videos(channel_id, user_id, exclude_analysis_id, limit)
        if not histories:
            return {
                'previous_video_count': 0,
                'sentiment_trend': 'stable',
                'risk_trend': 'stable',
                'avg_sentiment_change': 0.0,
                'avg_risk_change': 0.0,
                'entity_count_trend': 0,
            }

        sentiments = [h.avg_sentiment or 0.0 for h in reversed(histories)]
        risks = [h.avg_risk or 0.0 for h in reversed(histories)]
        entity_counts = [h.entity_count or 0 for h in reversed(histories)]

        if len(sentiments) < 2:
            return {
                'previous_video_count': len(histories),
                'sentiment_trend': 'stable',
                'risk_trend': 'stable',
                'avg_sentiment_change': 0.0,
                'avg_risk_change': 0.0,
                'entity_count_trend': 0,
            }

        first_half_sent = sum(sentiments[:len(sentiments)//2]) / max(len(sentiments)//2, 1)
        second_half_sent = sum(sentiments[len(sentiments)//2:]) / max(len(sentiments) - len(sentiments)//2, 1)
        first_half_risk = sum(risks[:len(risks)//2]) / max(len(risks)//2, 1)
        second_half_risk = sum(risks[len(risks)//2:]) / max(len(risks) - len(risks)//2, 1)

        sent_change = second_half_sent - first_half_sent
        risk_change = second_half_risk - first_half_risk

        sent_trend = 'improving' if sent_change > 5 else 'declining' if sent_change < -5 else 'stable'
        risk_trend = 'improving' if risk_change < -5 else 'declining' if risk_change > 5 else 'stable'

        entity_trend = entity_counts[-1] - entity_counts[0] if len(entity_counts) > 1 else 0

        return {
            'previous_video_count': len(histories),
            'sentiment_trend': sent_trend,
            'risk_trend': risk_trend,
            'avg_sentiment_change': round(sent_change, 1),
            'avg_risk_change': round(risk_change, 1),
            'entity_count_trend': entity_trend,
        }
