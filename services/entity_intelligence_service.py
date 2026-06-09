from models.entity import Entity


class EntityIntelligenceService:
    def __init__(self, resolution_service=None):
        from services.entity_resolution_service import EntityResolutionService
        self.resolver = resolution_service or EntityResolutionService()

    def compute_intelligence(self, extracted_entities, total_comments, total_segments):
        resolved = self.resolver.resolve(extracted_entities)
        max_freq = max((e['frequency'] for e in resolved), default=1)
        for entity in resolved:
            freq = entity['frequency']
            entity['importance_score'] = round(min(100, (freq / max_freq) * 100), 1)
            entity['relevance_score'] = self._compute_relevance(entity, total_comments, total_segments)
            entity['relationship'] = self._compute_relationship(entity)
        resolved.sort(key=lambda e: e['importance_score'], reverse=True)
        return resolved

    def _compute_relevance(self, entity, total_comments, total_segments):
        freq = entity['frequency']
        total = total_comments + total_segments
        if total == 0:
            return 0.0
        base = (freq / total) * 100
        return round(min(100, base * 1.5), 1)

    def _compute_relationship(self, entity):
        sources = entity.get('source', '')
        if sources == Entity.SOURCE_COMBINED:
            return 'discussed_across_sources'
        if sources == Entity.SOURCE_TRANSCRIPT:
            return 'discussed_in_transcript'
        if sources == Entity.SOURCE_COMMENT:
            return 'discussed_in_comments'
        if sources == Entity.SOURCE_TITLE:
            return 'mentioned_in_title'
        if sources == Entity.SOURCE_DESCRIPTION:
            return 'mentioned_in_description'
        return 'mentioned'
