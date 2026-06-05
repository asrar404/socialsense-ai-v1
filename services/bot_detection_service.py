import re
from collections import Counter


class BotDetectionService:
    GENERIC_PHRASES = [
        'great post', 'nice post', 'good post', 'thanks for sharing',
        'thank you for sharing', 'very informative', 'well said',
        'i agree', 'totally agree', 'completely agree',
        'this is great', 'this is awesome', 'this is amazing',
        'keep it up', 'keep up the good work',
        'looking forward to more', 'can\'t wait for more',
        'i love this', 'so true', 'very true',
        'thanks for the information', 'appreciate the share',
        'nice content', 'good content', 'great content',
    ]

    TEMPLATE_INDICATORS = [
        r'\b(first of all|secondly|thirdly|finally|in conclusion)\b',
        r'\b(in addition|furthermore|moreover|additionally)\b',
        r'\b(as mentioned|as stated|as noted)\b',
        r'\b(on the other hand|in contrast|however|nevertheless)\b',
        r'\b(it is important to note|it should be noted)\b',
        r'\b(the content is|the quality is|the information is)\b',
        r'\b(the discussion|the analysis|the review)\b',
        r'\b(overall|in summary|to summarize|in brief)\b',
    ]

    FORMALITY_MARKERS = [
        r'\b(indeed|thus|hence|thereby|hereby|wherein)\b',
        r'\b(heretofore|hereafter|thereafter|thereupon)\b',
        r'\b(pursuant|aforementioned|herein|therein)\b',
    ]

    @classmethod
    def analyze(cls, text, all_texts=None):
        if not text or not text.strip():
            return {
                'bot_score': 0.0,
                'confidence': 0.0,
                'bot_label': 'Low',
                'explanation': 'No text to analyze.',
            }

        reasons = []
        score = 0.0
        text_lower = text.lower()

        for phrase in cls.GENERIC_PHRASES:
            if phrase in text_lower:
                score += 15
                reasons.append('Contains generic/stock phrasing')
                break

        template_count = sum(1 for p in cls.TEMPLATE_INDICATORS if re.search(p, text_lower))
        if template_count >= 3:
            score += template_count * 8
            reasons.append('Template-like structural patterns detected')
        elif template_count >= 1:
            score += template_count * 5

        formality_count = sum(1 for p in cls.FORMALITY_MARKERS if re.search(p, text_lower))
        if formality_count > 0:
            score += formality_count * 10
            reasons.append('Excessive formal language not typical of human comments')

        words = text.split()
        if len(words) > 30:
            unique_ratio = len(set(w.lower() for w in words)) / max(len(words), 1)
            if unique_ratio < 0.5:
                score += 15
                reasons.append('Highly repetitive vocabulary suggests automation')

        sentences = re.split(r'[.!?]+', text)
        avg_sentence_len = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
        if avg_sentence_len > 25 and len(sentences) >= 3:
            score += 10
            reasons.append('Uniformly long sentences suggest AI generation')

        if all_texts:
            pair_count = 0
            for other in all_texts:
                if other != text and cls._jaccard_similarity(text, other) > 0.6:
                    pair_count += 1
            if pair_count >= 2:
                score += 15
                reasons.append('High similarity with multiple other comments (automation pattern)')

        bot_score = min(100.0, score)

        if bot_score <= 15:
            label = 'Low'
            explanation = 'Comment appears to be human-written.'
        elif bot_score <= 40:
            label = 'Medium'
            explanation = 'Some automated patterns detected but not conclusive.'
        elif bot_score <= 70:
            label = 'High'
            explanation = 'Strong indicators of automated or AI-generated content.'
        else:
            label = 'Critical'
            explanation = 'Very likely automated or AI-generated. High suspicion of bot activity.'

        if reasons:
            explanation = '; '.join(reasons) + '. ' + explanation

        disclaimer = 'AI/Bot detection is probabilistic and should not be treated as proof.'
        explanation = explanation + ' ' + disclaimer

        confidence = min(0.90, 0.3 + (bot_score / 100.0) * 0.6)

        return {
            'bot_score': round(bot_score, 1),
            'confidence': round(confidence, 2),
            'bot_label': label,
            'explanation': explanation,
        }

    @classmethod
    def _jaccard_similarity(cls, t1, t2):
        words1 = set(t1.lower().split())
        words2 = set(t2.lower().split())
        if not words1 and not words2:
            return 1.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / max(len(union), 1)
