from flask import current_app
from services.entity_history_service import EntityHistoryService
from services.video_history_service import VideoHistoryService


class VideoComparisonService:
    def __init__(self):
        self.entity_history = EntityHistoryService()
        self.video_history = VideoHistoryService()

    def compare_with_channel_average(self, channel_id, user_id, current_sentiment,
                                     current_risk, current_entity_count):
        channel_histories = self.video_history.get_previous_videos(
            channel_id, user_id, limit=50
        )
        if not channel_histories:
            return {
                'has_history': False,
                'sentiment_vs_avg': 0.0,
                'risk_vs_avg': 0.0,
                'entity_count_vs_avg': 0.0,
                'channel_avg_sentiment': 0.0,
                'channel_avg_risk': 0.0,
                'channel_avg_entity_count': 0.0,
            }

        avg_sent = sum(h.avg_sentiment or 0.0 for h in channel_histories) / len(channel_histories)
        avg_risk = sum(h.avg_risk or 0.0 for h in channel_histories) / len(channel_histories)
        avg_entity = sum(h.entity_count or 0 for h in channel_histories) / len(channel_histories)

        return {
            'has_history': True,
            'sentiment_vs_avg': round(current_sentiment - avg_sent, 1),
            'risk_vs_avg': round(current_risk - avg_risk, 1),
            'entity_count_vs_avg': round(current_entity_count - avg_entity, 1),
            'channel_avg_sentiment': round(avg_sent, 1),
            'channel_avg_risk': round(avg_risk, 1),
            'channel_avg_entity_count': round(avg_entity, 1),
        }

    def compare_with_top_video(self, channel_id, user_id, current_sentiment,
                               current_risk, current_entity_count):
        top_videos = self.video_history.get_previous_videos(
            channel_id, user_id, limit=5
        )
        if not top_videos:
            return {
                'has_history': False,
                'top_video_title': None,
                'sentiment_vs_top': 0.0,
                'risk_vs_top': 0.0,
                'entity_count_vs_top': 0.0,
            }

        best = max(top_videos, key=lambda h: h.avg_sentiment or 0)
        return {
            'has_history': True,
            'top_video_title': best.video_title,
            'sentiment_vs_top': round(current_sentiment - (best.avg_sentiment or 0), 1),
            'risk_vs_top': round(current_risk - (best.avg_risk or 0), 1),
            'entity_count_vs_top': round(current_entity_count - (best.entity_count or 0), 1),
        }
