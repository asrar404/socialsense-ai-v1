class RiskEngine:
    RISK_THRESHOLDS = {
        'sentiment': {
            'low': (50, 65),
            'negative_bonus': 15,
        },
        'toxicity': {
            'low': 15,
            'medium': 40,
            'high': 70,
        },
        'spam': {
            'low': 15,
            'medium': 40,
            'high': 70,
        },
        'bot': {
            'low': 15,
            'medium': 40,
            'high': 70,
        },
    }

    WEIGHTS = {
        'toxicity': 0.35,
        'spam': 0.25,
        'bot': 0.20,
        'negative_sentiment': 0.10,
        'duplicate': 0.10,
    }

    @classmethod
    def calculate(cls, sentiment, toxicity, spam, bot, duplicate_score=0.0):
        reasons = []
        recommendation_parts = []

        sentiment_score = sentiment.get('score', 50.0)
        sentiment_is_negative = sentiment.get('label', 'Neutral') == 'Negative'
        negative_severity = 0.0
        if sentiment_is_negative:
            negative_severity = (50.0 - sentiment_score) / 50.0 * 100.0

        tox = toxicity.get('toxicity_score', 0.0)
        sp = spam.get('spam_score', 0.0)
        bt = bot.get('bot_score', 0.0)

        weighted = (
            cls.WEIGHTS['toxicity'] * tox +
            cls.WEIGHTS['spam'] * sp +
            cls.WEIGHTS['bot'] * bt +
            cls.WEIGHTS['negative_sentiment'] * negative_severity +
            cls.WEIGHTS['duplicate'] * duplicate_score
        )

        final_score = min(100.0, weighted)

        if tox >= cls.RISK_THRESHOLDS['toxicity']['high']:
            reasons.append('Toxic language detected')
        elif tox >= cls.RISK_THRESHOLDS['toxicity']['medium']:
            reasons.append('Mild toxic language')

        if sp >= cls.RISK_THRESHOLDS['spam']['high']:
            reasons.append('Spam links detected')
        elif sp >= cls.RISK_THRESHOLDS['spam']['medium']:
            reasons.append('Spam patterns detected')

        if bt >= cls.RISK_THRESHOLDS['bot']['high']:
            reasons.append('Automated/bot-like content detected')
        elif bt >= cls.RISK_THRESHOLDS['bot']['medium']:
            reasons.append('Possible automated patterns')

        if sentiment_is_negative and sentiment_score < 30:
            reasons.append('Strongly negative sentiment')

        if duplicate_score >= 50:
            reasons.append('Repeated comment pattern')

        if final_score <= 15:
            label = 'Low'
            recommendation = 'No action needed. Comment appears safe.'
        elif final_score <= 40:
            label = 'Medium'
            recommendation = 'Monitor comment. Some concerning patterns detected.'
        elif final_score <= 70:
            label = 'High'
            recommendation = 'Review comments manually and consider moderation.'
            recommendation_parts.append('Review')
        else:
            label = 'Critical'
            recommendation = 'Immediate review recommended. High likelihood of harmful content.'
            recommendation_parts.append('Immediate Review')

        if 'Toxic' in ''.join(reasons):
            if 'Review' not in recommendation_parts:
                recommendation_parts.append('Review')

        if recommendation_parts:
            recommendation = ' '.join(recommendation_parts) + ' recommended. ' + recommendation

        confidence = min(0.95, 0.4 + (final_score / 100.0) * 0.55)

        return {
            'final_risk_score': round(final_score, 1),
            'final_risk_label': label,
            'confidence': round(confidence, 2),
            'reasons': reasons if reasons else ['No significant risk factors detected'],
            'recommendation': recommendation,
        }
