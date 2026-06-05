import re
from collections import Counter


class SpamService:
    PROMOTIONAL_PHRASES = [
        r'\b(check\s+(out|this))\b',
        r'\b(click\s+(here|this|the\s+link))\b',
        r'\b(subscribe|follow|like|share)\b',
        r'\b(buy\s+now|order\s+now|shop\s+now)\b',
        r'\b(limited\s+(time|offer|edition))\b',
        r'\b(don\'?t\s+miss\s+out)\b',
        r'\b(act\s+now|hurry)\b',
        r'\b(free\s+(trial|offer|download|money))\b',
        r'\b(click\s+below|link\s+in\s+(bio|description))\b',
        r'\b(visit\s+(my|our))\b',
        r'\b(sign\s+up|register\s+now)\b',
        r'\b(exclusive\s+(offer|deal|access))\b',
        r'\b(win\s+(a|a\s+free|prize))\b',
        r'\b(make\s+money|earn\s+money|get\s+rich)\b',
        r'\b(work\s+from\s+home)\b',
    ]

    URL_PATTERN = re.compile(r'https?://[^\s]+|www\.[^\s]+')

    EXCESSIVE_CAPS_PATTERN = re.compile(r'[A-Z]{3,}')

    EMOJI_PATTERN = re.compile(r'[\U0001F300-\U0001F9FF\u2600-\u27BF\uFE00-\uFE0F]')

    REPEATED_PATTERN = re.compile(r'(.)\1{4,}')

    SCAM_KEYWORDS = [
        'guaranteed', 'congratulations', 'you won', 'you\'ve won',
        'selected', 'winner', 'cash prize', 'lottery', 'million',
        'billion', 'inheritance', 'wire transfer', 'western union',
        'money gram', 'bitcoin', 'crypto', 'investment opportunity',
        'double your', 'risk free', 'no risk', '100%',
    ]

    @classmethod
    def analyze(cls, text, all_texts=None):
        if not text or not text.strip():
            return {
                'spam_score': 0.0,
                'confidence': 0.0,
                'spam_label': 'Low',
                'explanation': 'No text to analyze.',
            }

        reasons = []
        score = 0.0
        text_lower = text.lower()

        promo_count = 0
        for phrase in cls.PROMOTIONAL_PHRASES:
            if re.search(phrase, text_lower, re.IGNORECASE):
                promo_count += 1
        if promo_count > 0:
            score += promo_count * 12
            if promo_count == 1:
                reasons.append('Promotional language detected')
            else:
                reasons.append(f'Multiple promotional phrases detected ({promo_count})')

        urls = cls.URL_PATTERN.findall(text)
        if urls:
            score += len(urls) * 15
            reasons.append(f'Suspicious links detected ({len(urls)})')

        caps_words = cls.EXCESSIVE_CAPS_PATTERN.findall(text)
        if len(caps_words) >= 2 or any(len(w) >= 5 for w in caps_words):
            score += 10
            reasons.append('Excessive capitalization detected')

        emojis = cls.EMOJI_PATTERN.findall(text)
        if len(emojis) >= 5:
            score += 8
            reasons.append('Excessive emoji usage detected')

        repeated = cls.REPEATED_PATTERN.findall(text)
        if repeated:
            score += 8
            reasons.append('Suspicious repeated character patterns')

        scam_count = sum(1 for kw in cls.SCAM_KEYWORDS if kw in text_lower)
        if scam_count > 0:
            score += scam_count * 10
            reasons.append('Scam-like language detected')

        keyword_stuffing = len(text.split()) > 20 and len(set(text.split())) / max(len(text.split()), 1) < 0.5
        if keyword_stuffing:
            score += 15
            reasons.append('Keyword stuffing detected')

        if all_texts:
            total_others = len(all_texts) - 1
            if total_others > 0:
                exact_dupes = sum(1 for t in all_texts if t == text) - 1
                similar_count = sum(1 for t in all_texts if t != text and cls._text_similarity(text, t) > 0.8)
                total_similar = exact_dupes + similar_count
                if total_similar >= 2:
                    score += 15
                    reasons.append('Content appears in multiple comments (possible copypasta/spam)')

        spam_score = min(100.0, score)

        if spam_score <= 15:
            label = 'Low'
            explanation = 'No significant spam indicators detected.'
        elif spam_score <= 40:
            label = 'Medium'
            explanation = 'Mild spam patterns detected.'
        elif spam_score <= 70:
            label = 'High'
            explanation = 'Significant spam characteristics detected.'
        else:
            label = 'Critical'
            explanation = 'Strong spam indicators present. Likely automated or promotional.'

        if reasons:
            explanation = '; '.join(reasons) + '. ' + explanation

        confidence = min(0.95, 0.3 + (spam_score / 100.0) * 0.65)

        return {
            'spam_score': round(spam_score, 1),
            'confidence': round(confidence, 2),
            'spam_label': label,
            'explanation': explanation,
        }

    @classmethod
    def _text_similarity(cls, t1, t2):
        words1 = set(t1.lower().split())
        words2 = set(t2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        return len(intersection) / max(len(words1), len(words2))
