import re


class EntityRiskService:
    TARGETING_PATTERNS = [
        re.compile(r'(?:hate|attack|kill|destroy|ruin|hurt|die)\s+(?:you|him|her|them|this\s+\w+)'),
        re.compile(r'(?:you|he|she|they)\s+(?:should|must|need to)\s+(?:die|kill|hurt|stop)'),
    ]

    HARASSMENT_KEYWORDS = {'idiot', 'moron', 'stupid', 'jerk', 'loser', 'hate', 'terrible',
                           'disgusting', 'pathetic', 'worthless', 'fraud', 'scam', 'fake',
                           'liar', 'nasty', 'horrible', 'awful', 'dumb', 'suck'}

    MISINFORMATION_INDICATORS = {'fake news', 'lie', 'lying', 'propaganda', 'conspiracy',
                                  'cover up', 'hoax', 'manipulated', 'deepfake', 'misleading'}

    SPAM_PATTERNS = [
        re.compile(r'(?:buy|click|subscribe|follow|check|visit)\s+(?:now|here|this|link|our)'),
        re.compile(r'(?:limited|exclusive|free)\s+(?:offer|deal|opportunity)'),
    ]

    COORDINATED_PATTERNS = [
        re.compile(r'(?:join|upvote|downvote|share|repost|spread)\s+this'),
        re.compile(r'(?:raid|brigade|army)\s+(?:coming|attacking|downvoting)'),
    ]

    def compute_entity_risk(self, entity_name, comment_text, comment_sentiment='neutral'):
        if not comment_text:
            return 0.0, ['No comment text to analyze']
        reasons = []
        risk = 0.0
        text_lower = comment_text.lower()
        entity_lower = entity_name.lower()
        if entity_lower not in text_lower:
            return 0.0, ['Entity not mentioned in this comment']
        for pattern in self.TARGETING_PATTERNS:
            if pattern.search(text_lower):
                risk += 35
                reasons.append('Comment contains targeted attack language')
        for kw in self.HARASSMENT_KEYWORDS:
            if kw in text_lower:
                risk += 10
                reasons.append(f'Contains harassment keyword "{kw}"')
                break
        for indicator in self.MISINFORMATION_INDICATORS:
            if indicator in text_lower:
                risk += 20
                reasons.append(f'Contains misinformation indicator "{indicator}"')
                break
        for pattern in self.SPAM_PATTERNS:
            if pattern.search(text_lower):
                risk += 15
                reasons.append('Comment contains spam-like promotional language')
        for pattern in self.COORDINATED_PATTERNS:
            if pattern.search(text_lower):
                risk += 25
                reasons.append('Comment suggests coordinated activity')
        if comment_sentiment and comment_sentiment.lower() == 'negative':
            risk += 5
        risk = min(100, risk)
        return round(risk, 1), reasons[:5] if reasons else ['Low risk comment']

    def compute_entity_risks(self, entities, comment_results):
        results = []
        for entity in entities:
            entity_risks = []
            total_risk = 0.0
            for cr in comment_results:
                text = cr.comment_text if hasattr(cr, 'comment_text') else cr.get('text', '')
                sentiment = cr.sentiment if hasattr(cr, 'sentiment') else cr.get('sentiment', 'neutral')
                risk, reasons = self.compute_entity_risk(entity['name'], text, sentiment)
                entity_risks.append({
                    'comment_result_id': cr.id if hasattr(cr, 'id') else cr.get('id'),
                    'risk_score': risk,
                    'reasons': reasons,
                })
                total_risk += risk
            avg_risk = round(total_risk / max(len(entity_risks), 1), 1)
            results.append({
                'entity_name': entity['name'],
                'average_risk_score': avg_risk,
                'details': entity_risks,
            })
        return results
