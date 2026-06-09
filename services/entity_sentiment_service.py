import re


class EntitySentimentService:
    POSITIVE_WORDS = {
        'great', 'amazing', 'excellent', 'good', 'love', 'best', 'awesome', 'fantastic',
        'brilliant', 'outstanding', 'wonderful', 'perfect', 'impressive', 'innovative',
        'helpful', 'useful', 'beautiful', 'superb', 'remarkable', 'exceptional',
    }

    NEGATIVE_WORDS = {
        'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'poor', 'disgusting',
        'dreadful', 'atrocious', 'lousy', 'appalling', 'abysmal', 'mediocre',
        'pathetic', 'useless', 'overrated', 'underwhelming', 'disappointing',
    }

    INTENSIFIERS = {
        'very', 'really', 'extremely', 'incredibly', 'absolutely', 'totally',
        'completely', 'highly', 'deeply', 'so', 'too', 'super', 'ultra',
    }

    NEGATION_WORDS = {
        'not', "n't", 'never', 'no', 'neither', 'nor', 'none', 'nothing',
        'nowhere', 'hardly', 'barely', 'scarcely', 'doesnt', 'dont', 'wont',
        'cant', 'isnt', 'wasnt', 'werent', 'havent', 'hasnt', 'hadnt',
    }

    def compute_entity_sentiment(self, entity_name, comment_text):
        if not comment_text:
            return 'neutral', 50.0, 'No comment text'
        entity_lower = entity_name.lower()
        comment_lower = comment_text.lower()
        mentions = self._find_mentions(entity_lower, comment_lower)
        if not mentions:
            return 'neutral', 50.0, 'Entity not mentioned in comment'
        scores = []
        reasons = []
        for mention_start, mention_end in mentions:
            surrounding = self._get_surrounding_text(comment_lower, mention_start, mention_end)
            sent_score, sent_label, reason = self._analyze_window(surrounding)
            scores.append(sent_score)
        avg_score = sum(scores) / len(scores)
        if avg_score > 60:
            overall = 'positive'
        elif avg_score < 40:
            overall = 'negative'
        else:
            overall = 'neutral'
        reason_parts = [r for r in reasons if r]
        return overall, round(avg_score, 1), '; '.join(reason_parts[:3]) if reason_parts else 'Neutral context'

    def _find_mentions(self, entity_lower, text):
        mentions = []
        pattern = re.compile(r'\b' + re.escape(entity_lower) + r'\b', re.IGNORECASE)
        for m in pattern.finditer(text):
            mentions.append((m.start(), m.end()))
        return mentions

    def _get_surrounding_text(self, text, start, end, window=40):
        left = max(0, start - window)
        right = min(len(text), end + window)
        return text[left:right]

    def _analyze_window(self, window_text):
        words = re.findall(r"[a-z']+", window_text.lower())
        score = 50.0
        reasons = []
        negation_active = False
        for word in words:
            if word in self.NEGATION_WORDS:
                negation_active = True
                continue
            multiplier = -1 if negation_active else 1
            intensifier_mult = 1.0
            if word in self.INTENSIFIERS:
                intensifier_mult = 1.5
                continue
            if word in self.POSITIVE_WORDS:
                change = 15 * intensifier_mult * multiplier
                score += change
                if multiplier < 0:
                    reasons.append(f"negated positive '{word}'")
                else:
                    reasons.append(f"positive '{word}'")
                negation_active = False
            elif word in self.NEGATIVE_WORDS:
                change = 15 * intensifier_mult * -multiplier
                score += change
                if multiplier < 0:
                    reasons.append(f"negated negative '{word}'")
                else:
                    reasons.append(f"negative '{word}'")
                negation_active = False
        score = max(0, min(100, score))
        if score > 60:
            label = 'positive'
        elif score < 40:
            label = 'negative'
        else:
            label = 'neutral'
        return score, label, '; '.join(reasons[:2]) if reasons else ''

    def compute_entity_sentiments(self, entities, comment_results):
        results = []
        for entity in entities:
            entity_sentiments = []
            for cr in comment_results:
                sentiment, score, reason = self.compute_entity_sentiment(
                    entity['name'], cr.comment_text if hasattr(cr, 'comment_text') else cr.get('text', '')
                )
                entity_sentiments.append({
                    'comment_result_id': cr.id if hasattr(cr, 'id') else cr.get('id'),
                    'sentiment': sentiment,
                    'score': score,
                    'reason': reason,
                })
            avg_score = round(sum(s['score'] for s in entity_sentiments) / max(len(entity_sentiments), 1), 1)
            if avg_score > 60:
                overall = 'positive'
            elif avg_score < 40:
                overall = 'negative'
            else:
                overall = 'neutral'
            results.append({
                'entity_name': entity['name'],
                'overall_sentiment': overall,
                'average_score': avg_score,
                'mentions': entity_sentiments,
            })
        return results
