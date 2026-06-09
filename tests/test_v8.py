import pytest
from datetime import datetime, timezone
from models.entity import Entity
from models.entity_mention import EntityMention
from models.entity_context import EntityContext


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TestEntityModel:
    def test_create_entity(self, app, db, analysis):
        e = Entity(
            analysis_id=analysis.id,
            name='Tesla',
            normalized_name='Tesla',
            entity_type=Entity.COMPANY,
            source=Entity.SOURCE_COMBINED,
            frequency=5,
            importance_score=75.0,
        )
        db.session.add(e)
        db.session.commit()
        assert e.id is not None
        assert e.name == 'Tesla'
        assert e.normalized_name == 'Tesla'
        assert e.entity_type == 'COMPANY'
        assert e.frequency == 5
        assert e.source == 'combined'

    def test_entity_defaults(self, app, db, analysis):
        e = Entity(analysis_id=analysis.id, name='Test', normalized_name='Test')
        db.session.add(e)
        db.session.commit()
        assert e.entity_type == 'OTHER'
        assert e.source == 'combined'
        assert e.frequency == 0
        assert e.importance_score == 0.0

    def test_entity_constants(self, app, db):
        assert Entity.PERSON == 'PERSON'
        assert Entity.COMPANY == 'COMPANY'
        assert Entity.PRODUCT == 'PRODUCT'
        assert Entity.ORGANIZATION == 'ORGANIZATION'
        assert Entity.LOCATION == 'LOCATION'
        assert Entity.EVENT == 'EVENT'
        assert Entity.TOPIC == 'TOPIC'
        assert Entity.OTHER == 'OTHER'
        assert Entity.SOURCE_COMBINED == 'combined'

    def test_entity_analysis_relationship(self, app, db, analysis):
        e = Entity(analysis_id=analysis.id, name='OpenAI', normalized_name='OpenAI', entity_type=Entity.ORGANIZATION)
        db.session.add(e)
        db.session.commit()
        assert e.analysis_id == analysis.id
        assert e in analysis.entities.all()

    def test_entity_repr(self, app, db, analysis):
        e = Entity(analysis_id=analysis.id, name='Google', normalized_name='Google', entity_type=Entity.COMPANY)
        db.session.add(e)
        db.session.commit()
        assert 'Google' in repr(e)
        assert 'COMPANY' in repr(e)

    def test_entity_cascade_delete(self, app, db, analysis):
        e = Entity(analysis_id=analysis.id, name='Microsoft', normalized_name='Microsoft')
        db.session.add(e)
        db.session.commit()
        eid = e.id
        db.session.delete(analysis)
        db.session.commit()
        assert Entity.query.get(eid) is None


class TestEntityMentionModel:
    def test_create_mention(self, app, db, analysis):
        e = Entity(analysis_id=analysis.id, name='Apple', normalized_name='Apple')
        db.session.add(e)
        db.session.commit()
        m = EntityMention(
            entity_id=e.id,
            mention_text='Apple',
            mention_source=EntityMention.MENTION_SOURCE_COMMENT,
            context_snippet='Apple makes great products',
        )
        db.session.add(m)
        db.session.commit()
        assert m.id is not None
        assert m.entity_id == e.id
        assert m.mention_text == 'Apple'

    def test_mention_defaults(self, app, db, analysis):
        e = Entity(analysis_id=analysis.id, name='Test', normalized_name='Test')
        db.session.add(e)
        db.session.commit()
        m = EntityMention(entity_id=e.id, mention_text='Test')
        db.session.add(m)
        db.session.commit()
        assert m.mention_source == 'comment'
        assert m.comment_result_id is None
        assert m.transcript_segment_id is None

    def test_mention_entity_relationship(self, app, db, analysis):
        e = Entity(analysis_id=analysis.id, name='Amazon', normalized_name='Amazon')
        db.session.add(e)
        db.session.commit()
        m = EntityMention(entity_id=e.id, mention_text='Amazon')
        db.session.add(m)
        db.session.commit()
        assert m.entity.name == 'Amazon'


class TestEntityContextModel:
    def test_create_context(self, app, db, analysis):
        from models.comment_result import CommentResult
        e = Entity(analysis_id=analysis.id, name='Netflix', normalized_name='Netflix')
        db.session.add(e)
        db.session.commit()
        cr = CommentResult(analysis_id=analysis.id, comment_text='Netflix is great')
        db.session.add(cr)
        db.session.commit()
        ec = EntityContext(
            entity_id=e.id,
            comment_result_id=cr.id,
            entity_sentiment='positive',
            entity_sentiment_score=75.0,
            entity_risk_score=10.0,
            entity_relevance_score=80.0,
            entity_context_label=EntityContext.LABEL_HIGHLY_RELATED,
            reason='Positive mention in comment',
        )
        db.session.add(ec)
        db.session.commit()
        assert ec.id is not None
        assert ec.entity_sentiment == 'positive'
        assert ec.entity_context_label == 'highly_related'

    def test_context_defaults(self, app, db, analysis):
        from models.comment_result import CommentResult
        e = Entity(analysis_id=analysis.id, name='Test', normalized_name='Test')
        db.session.add(e)
        db.session.commit()
        cr = CommentResult(analysis_id=analysis.id, comment_text='test')
        db.session.add(cr)
        db.session.commit()
        ec = EntityContext(entity_id=e.id, comment_result_id=cr.id)
        db.session.add(ec)
        db.session.commit()
        assert ec.entity_sentiment_score == 0.0
        assert ec.entity_risk_score == 0.0
        assert ec.entity_relevance_score == 0.0
        assert ec.entity_context_label == 'unknown'

    def test_context_constants(self, app, db):
        assert EntityContext.LABEL_HIGHLY_RELATED == 'highly_related'
        assert EntityContext.LABEL_RELATED == 'related'
        assert EntityContext.LABEL_PARTIALLY_RELATED == 'partially_related'
        assert EntityContext.LABEL_UNRELATED == 'unrelated'
        assert EntityContext.LABEL_UNKNOWN == 'unknown'


class TestEntityExtractionService:
    def test_extract_person(self, app, db):
        from services.entity_extraction_service import EntityExtractionService
        svc = EntityExtractionService()
        result = svc.extract_from_texts(title='Elon Musk announces new product')
        names = [r['name'] for r in result]
        assert any('Elon' in n for n in names)

    def test_extract_from_title(self, app, db):
        from services.entity_extraction_service import EntityExtractionService
        svc = EntityExtractionService()
        result = svc.extract_from_texts(title='Tesla Inc unveils Model 3')
        names = [r['name'] for r in result]
        assert any('Tesla' in n for n in names)

    def test_extract_empty_texts(self, app, db):
        from services.entity_extraction_service import EntityExtractionService
        svc = EntityExtractionService()
        result = svc.extract_from_texts()
        assert result == []

    def test_extract_company_pattern(self, app, db):
        from services.entity_extraction_service import EntityExtractionService
        svc = EntityExtractionService()
        result = svc.extract_from_texts(description='MicrosoftCorp announced earnings')
        types = [r['entity_type'] for r in result]
        assert any(t == Entity.COMPANY for t in types)


class TestEntityResolutionService:
    def test_normalize_alias(self, app, db):
        from services.entity_resolution_service import EntityResolutionService
        svc = EntityResolutionService()
        assert svc.normalize('openai') == 'OpenAI'
        assert svc.normalize('Open AI') == 'OpenAI'
        assert svc.normalize('msft') == 'Microsoft'

    def test_normalize_unknown(self, app, db):
        from services.entity_resolution_service import EntityResolutionService
        svc = EntityResolutionService()
        assert svc.normalize('SomeRandomCompany') == 'SomeRandomCompany'

    def test_resolve_deduplicates(self, app, db):
        from services.entity_resolution_service import EntityResolutionService
        svc = EntityResolutionService()
        extracted = [
            {'name': 'OpenAI', 'entity_type': 'COMPANY', 'source': 'title', 'frequency': 2},
            {'name': 'openai', 'entity_type': 'COMPANY', 'source': 'comment', 'frequency': 1},
        ]
        resolved = svc.resolve(extracted)
        assert len(resolved) == 1
        assert resolved[0]['frequency'] == 3

    def test_add_alias(self, app, db):
        from services.entity_resolution_service import EntityResolutionService
        svc = EntityResolutionService()
        svc.add_alias('myco', 'MyCompany')
        assert svc.normalize('myco') == 'MyCompany'


class TestEntityIntelligenceService:
    def test_compute_importance(self, app, db):
        from services.entity_intelligence_service import EntityIntelligenceService
        svc = EntityIntelligenceService()
        extracted = [
            {'name': 'Tesla', 'entity_type': 'COMPANY', 'source': 'combined', 'frequency': 10},
            {'name': 'Elon Musk', 'entity_type': 'PERSON', 'source': 'transcript', 'frequency': 5},
        ]
        result = svc.compute_intelligence(extracted, 100, 50)
        assert len(result) == 2
        assert result[0]['importance_score'] >= result[1]['importance_score']

    def test_relationship_combined(self, app, db):
        from services.entity_intelligence_service import EntityIntelligenceService
        svc = EntityIntelligenceService()
        result = svc.compute_intelligence([{'name': 'Test', 'entity_type': 'OTHER', 'source': 'combined', 'frequency': 1}], 10, 5)
        assert result[0]['relationship'] == 'discussed_across_sources'

    def test_relationship_transcript(self, app, db):
        from services.entity_intelligence_service import EntityIntelligenceService
        svc = EntityIntelligenceService()
        result = svc.compute_intelligence([{'name': 'Test', 'entity_type': 'OTHER', 'source': 'transcript', 'frequency': 1}], 10, 5)
        assert result[0]['relationship'] == 'discussed_in_transcript'


class TestEntitySentimentService:
    def test_positive_sentiment(self, app, db):
        from services.entity_sentiment_service import EntitySentimentService
        svc = EntitySentimentService()
        sentiment, score, reason = svc.compute_entity_sentiment('Tesla', 'Tesla is amazing and great!')
        assert sentiment == 'positive'
        assert score > 60

    def test_negative_sentiment(self, app, db):
        from services.entity_sentiment_service import EntitySentimentService
        svc = EntitySentimentService()
        sentiment, score, reason = svc.compute_entity_sentiment('Tesla', 'Tesla is terrible and awful.')
        assert sentiment == 'negative'
        assert score < 40

    def test_neutral_sentiment(self, app, db):
        from services.entity_sentiment_service import EntitySentimentService
        svc = EntitySentimentService()
        sentiment, score, reason = svc.compute_entity_sentiment('Tesla', 'Tesla is a company.')
        assert sentiment == 'neutral'

    def test_entity_not_mentioned(self, app, db):
        from services.entity_sentiment_service import EntitySentimentService
        svc = EntitySentimentService()
        sentiment, score, reason = svc.compute_entity_sentiment('Tesla', 'I like Apple.')
        assert sentiment == 'neutral'
        assert 'not mentioned' in reason.lower()

    def test_empty_comment(self, app, db):
        from services.entity_sentiment_service import EntitySentimentService
        svc = EntitySentimentService()
        sentiment, score, reason = svc.compute_entity_sentiment('Tesla', '')
        assert sentiment == 'neutral'

    def test_negation_handling(self, app, db):
        from services.entity_sentiment_service import EntitySentimentService
        svc = EntitySentimentService()
        sentiment, score, reason = svc.compute_entity_sentiment('Tesla', 'Tesla is not bad')
        assert score >= 50

    def test_compute_entity_sentiments_batch(self, app, db, analysis):
        from services.entity_sentiment_service import EntitySentimentService
        from models.comment_result import CommentResult
        svc = EntitySentimentService()
        cr1 = CommentResult(analysis_id=analysis.id, comment_text='Tesla is great')
        db.session.add(cr1)
        db.session.commit()
        entities = [{'name': 'Tesla', 'entity_type': 'COMPANY', 'source': 'comment', 'frequency': 1}]
        results = svc.compute_entity_sentiments(entities, [cr1])
        assert len(results) == 1
        assert results[0]['entity_name'] == 'Tesla'


class TestEntityRiskService:
    def test_targeting_increases_risk(self, app, db):
        from services.entity_risk_service import EntityRiskService
        svc = EntityRiskService()
        risk, reasons = svc.compute_entity_risk('Elon Musk', 'I hate Elon Musk, you should die!')
        assert risk > 30
        assert any('attack' in r.lower() for r in reasons)

    def test_harassment_keywords(self, app, db):
        from services.entity_risk_service import EntityRiskService
        svc = EntityRiskService()
        risk, reasons = svc.compute_entity_risk('Elon Musk', 'Elon Musk is an idiot and a liar.')
        assert risk >= 10

    def test_entity_not_mentioned_no_risk(self, app, db):
        from services.entity_risk_service import EntityRiskService
        svc = EntityRiskService()
        risk, reasons = svc.compute_entity_risk('Tesla', 'I like Apple.')
        assert risk == 0.0

    def test_spam_pattern_increases_risk(self, app, db):
        from services.entity_risk_service import EntityRiskService
        svc = EntityRiskService()
        risk, reasons = svc.compute_entity_risk('Tesla', 'Buy Tesla now! Click this link!')
        assert risk > 10

    def test_risk_capped_at_100(self, app, db):
        from services.entity_risk_service import EntityRiskService
        svc = EntityRiskService()
        risk, reasons = svc.compute_entity_risk('Person', 'Person is an idiot, kill him, buy now click here, join this raid, fake news liar!')
        assert risk <= 100

    def test_compute_entity_risks_batch(self, app, db, analysis):
        from services.entity_risk_service import EntityRiskService
        from models.comment_result import CommentResult
        svc = EntityRiskService()
        cr1 = CommentResult(analysis_id=analysis.id, comment_text='Tesla is great')
        db.session.add(cr1)
        db.session.commit()
        entities = [{'name': 'Tesla', 'entity_type': 'COMPANY', 'source': 'comment', 'frequency': 1}]
        results = svc.compute_entity_risks(entities, [cr1])
        assert len(results) == 1


class TestEntitySummaryService:
    def test_summary_empty(self, app, db):
        from services.entity_summary_service import EntitySummaryService
        svc = EntitySummaryService()
        summary = svc.generate_summary([], [], [])
        assert summary['total_entities'] == 0
        assert summary['most_discussed_person'] is None

    def test_summary_with_entities(self, app, db, analysis):
        from services.entity_summary_service import EntitySummaryService
        svc = EntitySummaryService()
        e1 = Entity(analysis_id=analysis.id, name='Elon Musk', normalized_name='Elon Musk', entity_type=Entity.PERSON, frequency=10)
        e2 = Entity(analysis_id=analysis.id, name='Tesla', normalized_name='Tesla', entity_type=Entity.COMPANY, frequency=8)
        db.session.add_all([e1, e2])
        db.session.commit()
        summary = svc.generate_summary([e1, e2], [], [])
        assert summary['total_entities'] == 2
        assert summary['most_discussed_person'] == 'Elon Musk'
        assert summary['most_discussed_company'] == 'Tesla'

    def test_type_distribution(self, app, db, analysis):
        from services.entity_summary_service import EntitySummaryService
        svc = EntitySummaryService()
        e1 = Entity(analysis_id=analysis.id, name='P1', normalized_name='P1', entity_type=Entity.PERSON, frequency=5)
        e2 = Entity(analysis_id=analysis.id, name='C1', normalized_name='C1', entity_type=Entity.COMPANY, frequency=3)
        db.session.add_all([e1, e2])
        db.session.commit()
        summary = svc.generate_summary([e1, e2], [], [])
        assert summary['entity_type_distribution'].get('PERSON') == 5
        assert summary['entity_type_distribution'].get('COMPANY') == 3

    def test_most_controversial(self, app, db, analysis):
        from services.entity_summary_service import EntitySummaryService
        svc = EntitySummaryService()
        e1 = Entity(analysis_id=analysis.id, name='E1', normalized_name='E1', entity_type=Entity.PERSON, frequency=1)
        db.session.add(e1)
        db.session.commit()
        risks = [{'entity_name': 'E1', 'average_risk_score': 80.0}]
        sentiments = [{'entity_name': 'E1', 'overall_sentiment': 'negative', 'average_score': 20.0}]
        summary = svc.generate_summary([e1], sentiments, risks)
        assert summary['most_controversial_entity'] == 'E1'

    def test_summary_most_positive(self, app, db, analysis):
        from services.entity_summary_service import EntitySummaryService
        svc = EntitySummaryService()
        e = Entity(analysis_id=analysis.id, name='GoodCo', normalized_name='GoodCo', entity_type=Entity.COMPANY, frequency=1)
        db.session.add(e)
        db.session.commit()
        sentiments = [{'entity_name': 'GoodCo', 'overall_sentiment': 'positive', 'average_score': 95.0}]
        summary = svc.generate_summary([e], sentiments, [])
        assert summary['most_positive_entity'] == 'GoodCo'

    def test_summary_most_negative(self, app, db, analysis):
        from services.entity_summary_service import EntitySummaryService
        svc = EntitySummaryService()
        e = Entity(analysis_id=analysis.id, name='BadCo', normalized_name='BadCo', entity_type=Entity.COMPANY, frequency=1)
        db.session.add(e)
        db.session.commit()
        sentiments = [{'entity_name': 'BadCo', 'overall_sentiment': 'negative', 'average_score': 10.0}]
        summary = svc.generate_summary([e], sentiments, [])
        assert summary['most_negative_entity'] == 'BadCo'

    def test_summary_most_discussed_product(self, app, db, analysis):
        from services.entity_summary_service import EntitySummaryService
        svc = EntitySummaryService()
        e = Entity(analysis_id=analysis.id, name='iPhone', normalized_name='iPhone', entity_type=Entity.PRODUCT, frequency=5)
        db.session.add(e)
        db.session.commit()
        summary = svc.generate_summary([e], [], [])
        assert summary['most_discussed_product'] == 'iPhone'


class TestEntityExtractionEdgeCases:
    def test_extract_with_transcript_and_comments(self, app, db):
        from services.entity_extraction_service import EntityExtractionService
        svc = EntityExtractionService()
        result = svc.extract_from_texts(
            title='Review',
            transcript_text='Tesla Model 3 is great',
            comments=[{'text': 'I love my Tesla'}],
        )
        assert len(result) > 0

    def test_extract_no_duplicates(self, app, db):
        from services.entity_extraction_service import EntityExtractionService
        svc = EntityExtractionService()
        result = svc.extract_from_texts(
            title='Tesla Tesla Tesla',
            comments=[{'text': 'Tesla is great'}, {'text': 'Tesla is bad'}],
        )
        names = [r['name'].lower() for r in result]
        assert names.count('tesla') <= 1

    def test_extract_source_combined(self, app, db):
        from services.entity_extraction_service import EntityExtractionService
        svc = EntityExtractionService()
        result = svc.extract_from_texts(
            title='Tesla',
            description='Tesla Inc',
        )
        combined = [r for r in result if r['source'] == 'combined']
        assert len(combined) > 0

    def test_product_pattern_match(self, app, db):
        from services.entity_extraction_service import EntityExtractionService
        svc = EntityExtractionService()
        result = svc.extract_from_texts(description='iPhone is great')
        types = [r['entity_type'] for r in result]
        assert Entity.PRODUCT in types


class TestEntityRiskEdgeCases:
    def test_empty_comment_no_risk(self, app, db):
        from services.entity_risk_service import EntityRiskService
        svc = EntityRiskService()
        risk, reasons = svc.compute_entity_risk('Tesla', '')
        assert risk == 0.0

    def test_misinformation_indicator(self, app, db):
        from services.entity_risk_service import EntityRiskService
        svc = EntityRiskService()
        risk, reasons = svc.compute_entity_risk('News', 'News is fake news propaganda')
        assert risk >= 20
        assert any('misinformation' in r.lower() for r in reasons)

    def test_coordinated_activity(self, app, db):
        from services.entity_risk_service import EntityRiskService
        svc = EntityRiskService()
        risk, reasons = svc.compute_entity_risk('Post', 'Upvote this Post and share this')
        assert risk >= 25
        assert any('coordinated' in r.lower() for r in reasons)

    def test_negative_sentiment_boost(self, app, db):
        from services.entity_risk_service import EntityRiskService
        svc = EntityRiskService()
        risk_neg, _ = svc.compute_entity_risk('X', 'X is bad.', comment_sentiment='negative')
        risk_neu, _ = svc.compute_entity_risk('X', 'X is bad.', comment_sentiment='neutral')
        assert risk_neg >= risk_neu
