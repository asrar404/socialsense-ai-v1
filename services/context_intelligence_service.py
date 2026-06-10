import json
from flask import current_app
from services.channel_context_service import ChannelContextService
from services.video_history_service import VideoHistoryService
from services.entity_history_service import EntityHistoryService
from services.topic_history_service import TopicHistoryService


class ContextIntelligenceService:
    def __init__(self):
        self.channel_service = ChannelContextService()
        self.video_history = VideoHistoryService()
        self.entity_history = EntityHistoryService()
        self.topic_history = TopicHistoryService()

    def compute_intelligence(self, user_id, channel_id, analysis_id,
                             entity_names=None, current_sentiment=50.0, current_risk=0.0):
        channel_data = self.channel_service.get_channel_intelligence(user_id, channel_id)
        trends = self.video_history.get_trend_statistics(channel_id, user_id, exclude_analysis_id=analysis_id)
        top_entities = self.entity_history.get_top_entities_by_channel(channel_id, user_id, limit=10)
        recurring_topics = self.topic_history.get_recurring_topics(channel_id, user_id, limit=10)

        historical_context_score = self._compute_historical_score(trends, channel_data)
        entity_recurrence_score = self._compute_entity_recurrence_score(
            entity_names or [], top_entities
        )
        topic_recurrence_score = self._compute_topic_recurrence_score(recurring_topics)
        channel_relevance_score = self._compute_channel_relevance(trends, channel_data)
        trend_score = self._compute_trend_score(trends)

        return {
            'historical_context': historical_context_score,
            'entity_recurrence': entity_recurrence_score,
            'topic_recurrence': topic_recurrence_score,
            'channel_relevance': channel_relevance_score,
            'trend_score': trend_score,
            'trend_direction': self._get_trend_direction(trends),
            'channel_data': channel_data,
            'trends': trends,
            'top_entities': top_entities,
            'recurring_topics': recurring_topics,
        }

    def _compute_historical_score(self, trends, channel_data):
        score = 0
        if channel_data['total_videos_analyzed'] > 0:
            score += 30
        if channel_data['total_videos_analyzed'] >= 5:
            score += 20
        elif channel_data['total_videos_analyzed'] >= 2:
            score += 10
        if channel_data['total_entities_detected'] > 0:
            score += 20
        if trends['previous_video_count'] > 0:
            score += 30
        return min(score, 100)

    def _compute_entity_recurrence_score(self, entity_names, top_entities):
        if not entity_names:
            return 0
        recurring = sum(
            1 for e in entity_names
            if any(te['normalized_name'].lower() == e.lower() for te in top_entities)
        )
        ratio = recurring / len(entity_names)
        return min(int(ratio * 100), 100)

    def _compute_topic_recurrence_score(self, recurring_topics):
        if not recurring_topics:
            return 0
        total_appearances = sum(t['appearances'] for t in recurring_topics)
        score = min(total_appearances * 10, 100)
        return score

    def _compute_channel_relevance(self, trends, channel_data):
        score = 0
        if channel_data['total_videos_analyzed'] >= 3:
            score += 40
        elif channel_data['total_videos_analyzed'] >= 1:
            score += 20
        if trends['previous_video_count'] >= 3:
            score += 30
        elif trends['previous_video_count'] >= 1:
            score += 15
        if channel_data['total_entities_detected'] >= 10:
            score += 30
        elif channel_data['total_entities_detected'] >= 5:
            score += 15
        return min(score, 100)

    def _compute_trend_score(self, trends):
        score = 50
        if trends.get('sentiment_trend') == 'improving':
            score += 20
        elif trends.get('sentiment_trend') == 'declining':
            score -= 20
        if trends.get('risk_trend') == 'improving':
            score += 15
        elif trends.get('risk_trend') == 'declining':
            score -= 15
        if trends.get('entity_count_trend', 0) > 0:
            score += 15
        return max(0, min(score, 100))

    def _get_trend_direction(self, trends):
        direction = 'stable'
        if trends.get('sentiment_trend') == 'improving' and trends.get('risk_trend') == 'improving':
            direction = 'positive'
        elif trends.get('sentiment_trend') == 'declining' or trends.get('risk_trend') == 'declining':
            direction = 'negative'
        elif trends.get('sentiment_trend') == 'improving':
            direction = 'positive'
        return direction
