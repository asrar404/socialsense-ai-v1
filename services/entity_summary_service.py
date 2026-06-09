import json
from models.entity import Entity


class EntitySummaryService:
    def generate_summary(self, entities, entity_sentiments, entity_risks):
        if not entities:
            return {
                'total_entities': 0,
                'most_discussed_person': None,
                'most_discussed_company': None,
                'most_discussed_product': None,
                'most_controversial_entity': None,
                'most_positive_entity': None,
                'most_negative_entity': None,
                'entity_type_distribution': {},
            }
        people = [e for e in entities if e.entity_type == Entity.PERSON]
        companies = [e for e in entities if e.entity_type in (Entity.COMPANY, Entity.ORGANIZATION)]
        products = [e for e in entities if e.entity_type == Entity.PRODUCT]
        most_discussed_person = max(people, key=lambda e: e.frequency).normalized_name if people else None
        most_discussed_company = max(companies, key=lambda e: e.frequency).normalized_name if companies else None
        most_discussed_product = max(products, key=lambda e: e.frequency).normalized_name if products else None
        type_dist = {}
        for e in entities:
            type_dist[e.entity_type] = type_dist.get(e.entity_type, 0) + e.frequency
        most_controversial = None
        most_positive = None
        most_negative = None
        if entity_risks:
            sorted_risks = sorted(entity_risks, key=lambda r: r['average_risk_score'], reverse=True)
            if sorted_risks and sorted_risks[0]['average_risk_score'] > 0:
                most_controversial = sorted_risks[0]['entity_name']
        if entity_sentiments:
            positive = [s for s in entity_sentiments if s['overall_sentiment'] == 'positive']
            negative = [s for s in entity_sentiments if s['overall_sentiment'] == 'negative']
            if positive:
                most_positive = max(positive, key=lambda s: s['average_score'])['entity_name']
            if negative:
                most_negative = min(negative, key=lambda s: s['average_score'])['entity_name']
        return {
            'total_entities': len(entities),
            'most_discussed_person': most_discussed_person,
            'most_discussed_company': most_discussed_company,
            'most_discussed_product': most_discussed_product,
            'most_controversial_entity': most_controversial,
            'most_positive_entity': most_positive,
            'most_negative_entity': most_negative,
            'entity_type_distribution': type_dist,
        }
