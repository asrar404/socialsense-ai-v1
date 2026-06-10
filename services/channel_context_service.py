from datetime import datetime, timezone
from flask import current_app
from database import db
from models.channel_context import ChannelContext
from models.video_context_history import VideoContextHistory
from models.entity_history import EntityHistory


class ChannelContextService:
    def get_or_create_channel(self, user_id, channel_id, channel_name=None):
        channel = ChannelContext.query.filter_by(
            user_id=user_id, channel_id=channel_id
        ).first()
        if not channel:
            channel = ChannelContext(
                user_id=user_id,
                channel_id=channel_id,
                channel_name=channel_name or 'Unknown',
            )
            db.session.add(channel)
            db.session.commit()
        return channel

    def update_channel_stats(self, user_id, channel_id):
        histories = VideoContextHistory.query.filter_by(
            user_id=user_id, channel_id=channel_id
        ).all()
        channel = self.get_or_create_channel(user_id, channel_id)

        total_videos = len(histories)
        total_entities = sum(h.entity_count or 0 for h in histories)
        avg_sent = 0.0
        avg_risk = 0.0
        if histories:
            avg_sent = sum(h.avg_sentiment or 0.0 for h in histories) / len(histories)
            avg_risk = sum(h.avg_risk or 0.0 for h in histories) / len(histories)

        channel.total_videos_analyzed = total_videos
        channel.total_entities_detected = total_entities
        channel.avg_sentiment = round(avg_sent, 1)
        channel.avg_risk = round(avg_risk, 1)
        db.session.commit()
        return channel

    def get_channel_intelligence(self, user_id, channel_id):
        channel = ChannelContext.query.filter_by(
            user_id=user_id, channel_id=channel_id
        ).first()
        if not channel:
            return {
                'total_videos_analyzed': 0,
                'total_entities_detected': 0,
                'avg_sentiment': 0.0,
                'avg_risk': 0.0,
            }
        return {
            'total_videos_analyzed': channel.total_videos_analyzed or 0,
            'total_entities_detected': channel.total_entities_detected or 0,
            'avg_sentiment': channel.avg_sentiment or 0.0,
            'avg_risk': channel.avg_risk or 0.0,
        }

    def get_all_channel_intelligence(self, user_id):
        channels = ChannelContext.query.filter_by(user_id=user_id).all()
        return [
            {
                'channel_id': c.channel_id,
                'channel_name': c.channel_name or 'Unknown',
                'total_videos_analyzed': c.total_videos_analyzed or 0,
                'total_entities_detected': c.total_entities_detected or 0,
                'avg_sentiment': c.avg_sentiment or 0.0,
                'avg_risk': c.avg_risk or 0.0,
            }
            for c in channels
        ]
