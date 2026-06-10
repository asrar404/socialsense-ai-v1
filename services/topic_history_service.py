from flask import current_app
from database import db
from models.video_context_history import VideoContextHistory
from models.video_transcript import VideoTranscript


class TopicHistoryService:
    def get_recurring_topics(self, channel_id, user_id, limit=20):
        transcripts = VideoTranscript.query.join(
            VideoContextHistory,
            VideoTranscript.youtube_analysis.has(
                analysis_id=VideoContextHistory.analysis_id
            )
        ).filter(
            VideoContextHistory.channel_id == channel_id,
            VideoContextHistory.user_id == user_id,
            VideoTranscript.topics.isnot(None),
            VideoTranscript.topics != '',
        ).order_by(VideoContextHistory.processed_at.desc()).limit(limit).all()

        topic_counts = {}
        for t in transcripts:
            if t.topics:
                for topic in t.topics.split(', '):
                    topic = topic.strip().lower()
                    if topic:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1

        sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {'topic': topic, 'appearances': count}
            for topic, count in sorted_topics[:limit]
        ]

    def get_topic_trend(self, topic_name, channel_id, user_id, limit=20):
        transcripts = VideoTranscript.query.join(
            VideoContextHistory,
            VideoTranscript.youtube_analysis.has(
                analysis_id=VideoContextHistory.analysis_id
            )
        ).filter(
            VideoContextHistory.channel_id == channel_id,
            VideoContextHistory.user_id == user_id,
            VideoTranscript.topics.isnot(None),
            VideoTranscript.topics.ilike(f'%{topic_name}%'),
        ).order_by(VideoContextHistory.processed_at.asc()).limit(limit).all()

        return [
            {
                'video_title': t.video_context_history.video_title if t.video_context_history else None,
                'processed_at': t.video_context_history.processed_at.isoformat() if t.video_context_history and t.video_context_history.processed_at else None,
            }
            for t in transcripts
        ]
