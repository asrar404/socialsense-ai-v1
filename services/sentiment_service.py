import re


class SentimentService:
    POSITIVE_WORDS = {
        'good', 'great', 'awesome', 'amazing', 'excellent', 'fantastic',
        'wonderful', 'brilliant', 'outstanding', 'superb', 'perfect',
        'love', 'beautiful', 'incredible', 'best', 'impressive',
        'fantastic', 'terrific', 'splendid', 'marvelous', 'fabulous',
        'nice', 'happy', 'glad', 'thankful', 'grateful', 'helpful',
        'informative', 'insightful', 'useful', 'valuable', 'clear',
        'concise', 'educational', 'brilliant', 'enjoyed', 'appreciate',
        'excited', 'wonderful', 'beautiful', 'lovely', 'delightful',
        'pleased', 'satisfied', 'impressed', 'recommend', 'supportive',
    }

    NEGATIVE_WORDS = {
        'bad', 'terrible', 'awful', 'horrible', 'worst', 'hate',
        'disgusting', 'pathetic', 'useless', 'stupid', 'dumb',
        'boring', 'waste', 'garbage', 'trash', 'pathetic',
        'annoying', 'frustrating', 'disappointing', 'mediocre',
        'poor', 'inferior', 'lousy', 'dreadful', 'abysmal',
        'ridiculous', 'absurd', 'shameful', 'disgrace', 'horrific',
        'atrocious', 'appalling', 'deplorable', 'contemptible',
        'despicable', 'vile', 'nasty', 'cruel', 'brutal', 'vulgar',
    }

    INTENSIFIERS = {'very', 'really', 'extremely', 'incredibly', 'absolutely', 'totally', 'completely', 'highly'}

    NEGATION_WORDS = {'not', "n't", 'never', 'neither', 'nor', 'no', 'nobody', 'nothing', 'nowhere', "don't", "doesn't", "didn't", "won't", "wouldn't", "shouldn't", "couldn't", "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't", "hadn't", "can't", "cannot"}

    @classmethod
    def analyze(cls, text):
        if not text or not text.strip():
            return {
                'score': 0.0,
                'confidence': 0.0,
                'label': 'Neutral',
                'explanation': 'No text to analyze.',
            }

        text_lower = text.lower()
        words = re.findall(r"[a-z']+", text_lower)

        positive_count = 0
        negative_count = 0
        negation_active = False
        intensity = 1.0
        total_weight = 0

        for word in words:
            if word in cls.NEGATION_WORDS:
                negation_active = True
                continue
            if word in cls.INTENSIFIERS:
                intensity = 1.5
                continue

            weight = intensity
            if negation_active:
                negation_active = False

            if word in cls.POSITIVE_WORDS:
                positive_count += weight
                total_weight += weight
            elif word in cls.NEGATIVE_WORDS:
                negative_count += weight
                total_weight += weight

            intensity = 1.0

        total = positive_count + negative_count
        if total == 0:
            return {
                'score': 50.0,
                'confidence': 0.3,
                'label': 'Neutral',
                'explanation': 'No strong sentiment words detected. The comment appears neutral in tone.',
            }

        raw_score = 50.0 + ((positive_count - negative_count) / total) * 50.0
        score = max(0.0, min(100.0, raw_score))

        confidence = min(0.95, 0.3 + (total_weight / (total_weight + 5)) * 0.65)

        if score >= 65:
            label = 'Positive'
            if positive_count > negative_count * 3:
                explanation = 'Contains strongly positive language and supportive wording.'
            else:
                explanation = 'Contains several positive words and supportive language.'
        elif score <= 35:
            label = 'Negative'
            if negative_count > positive_count * 3:
                explanation = 'Contains strongly negative language and harsh criticism.'
            else:
                explanation = 'Contains negative emotional language and criticism.'
        else:
            label = 'Neutral'
            explanation = 'Sentiment appears balanced or neutral with no strong emotional tone.'

        return {
            'score': round(score, 1),
            'confidence': round(confidence, 2),
            'label': label,
            'explanation': explanation,
        }
