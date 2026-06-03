import re
import math


class RiskScoringService:

    @staticmethod
    def calculate_spam_score(text):
        score = 0
        reasons = []
        text_lower = text.lower()

        link_count = len(re.findall(r'https?://\S+', text))
        if link_count > 0:
            score += link_count * 15
            reasons.append(f"Contains {link_count} link(s)")

        promo_words = ['buy', 'check out', 'subscribe', 'click here', 'limited offer',
                       'free', 'act now', 'don\'t miss', 'sign up', 'visit']
        promo_count = sum(1 for w in promo_words if w in text_lower)
        if promo_count > 0:
            score += promo_count * 10
            reasons.append(f"Contains {promo_count} promotional word(s)")

        words = text_lower.split()
        if len(words) > 5:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.4:
                score += 25
                reasons.append("Highly repetitive content")

        repeated_phrases = re.findall(r'(\b\w+\b)(?:\s+\1){2,}', text_lower)
        if repeated_phrases:
            score += 20
            reasons.append("Contains repetitive phrases")

        engagement_bait = ['like', 'share', 'comment', 'sub', 'follow', 'tag']
        bait_count = sum(1 for w in engagement_bait if w in text_lower.split())
        if bait_count > 2:
            score += bait_count * 5
            reasons.append("Engagement bait detected")

        all_caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if all_caps_ratio > 0.6 and len(text) > 10:
            score += 15
            reasons.append("Excessive use of capital letters")

        score = min(score, 100)

        if not reasons:
            reasons.append("No spam indicators detected")

        return {
            'score': round(score, 1),
            'explanation': '; '.join(reasons),
        }

    @staticmethod
    def calculate_toxicity_score(text):
        score = 0
        reasons = []
        text_lower = text.lower()

        aggressive_words = ['hate', 'stupid', 'idiot', 'dumb', 'worst', 'terrible',
                            'horrible', 'awful', 'disgusting', 'pathetic', 'useless']
        aggressive_count = sum(1 for w in aggressive_words if w in text_lower.split())
        if aggressive_count > 0:
            score += aggressive_count * 15
            reasons.append(f"Contains {aggressive_count} aggressive word(s)")

        profanity_patterns = [
            r'\bf+u+[ck]\b', r'\bs+h+i+t\b', r'\ba+s+s\b', r'\bd+a+m+n\b',
        ]
        profanity_count = sum(1 for p in profanity_patterns if re.search(p, text_lower))
        if profanity_count > 0:
            score += 30
            reasons.append("Contains offensive language")

        exclamation_count = text.count('!')
        if exclamation_count > 3:
            score += min(exclamation_count * 5, 20)
            reasons.append(f"Excessive exclamation marks ({exclamation_count})")

        personal_attacks = ['you are', 'you\'re', 'ur', 'u r']
        attack_count = sum(1 for p in personal_attacks if re.search(rf'\b{p}\b.*\b(?:stupid|dumb|idiot|worst)\b', text_lower))
        if attack_count > 0:
            score += 20
            reasons.append("Potential personal attack detected")

        all_caps_words = [w for w in text.split() if len(w) > 2 and w.isupper()]
        if len(all_caps_words) > 2:
            score += 10
            reasons.append("Excessive shouting (ALL CAPS words)")

        score = min(score, 100)

        if not reasons:
            reasons.append("No toxicity indicators detected")

        return {
            'score': round(score, 1),
            'explanation': '; '.join(reasons),
        }

    @staticmethod
    def calculate_sentiment(text):
        text_lower = text.lower()
        words = text_lower.split()

        positive_words = ['great', 'awesome', 'amazing', 'excellent', 'fantastic',
                          'wonderful', 'love', 'perfect', 'best', 'beautiful',
                          'informative', 'helpful', 'thanks', 'thank', 'good',
                          'nice', 'brilliant', 'outstanding', 'incredible', 'superb']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'worst',
                          'hate', 'boring', 'stupid', 'dumb', 'useless',
                          'waste', 'disappointing', 'poor', 'pathetic', 'annoying']

        positive_count = sum(1 for w in positive_words if w in words)
        negative_count = sum(1 for w in negative_words if w in words)

        total = positive_count + negative_count
        if total == 0:
            return {
                'label': 'Neutral',
                'score': 50.0,
                'explanation': 'No strong positive or negative language detected.',
            }

        ratio = positive_count / total

        if ratio > 0.6:
            label = 'Positive'
            score = 50 + (ratio - 0.6) * 125
            explanation = f"Positive language detected ({positive_count} positive word(s))."
        elif ratio < 0.4:
            label = 'Negative'
            score = 50 - (0.4 - ratio) * 125
            explanation = f"Negative language detected ({negative_count} negative word(s))."
        else:
            label = 'Neutral'
            score = 50.0
            explanation = "Mixed or neutral sentiment."

        return {
            'label': label,
            'score': round(max(0, min(100, score)), 1),
            'explanation': explanation,
        }

    @staticmethod
    def calculate_duplicate_score(text, all_comments):
        score = 0
        reasons = []
        text_lower = text.lower().strip()

        exact_matches = sum(1 for c in all_comments if c.lower().strip() == text_lower) - 1
        if exact_matches > 0:
            score += exact_matches * 30
            reasons.append(f"Exact duplicate found ({exact_matches} other(s))")

        text_words = set(text_lower.split())
        if len(text_words) > 3:
            for comment in all_comments:
                if comment.lower().strip() == text_lower:
                    continue
                other_words = set(comment.lower().split())
                if len(text_words & other_words) / len(text_words) > 0.8:
                    score += 15
                    reasons.append("Very similar to another comment")
                    break

        score = min(score, 100)

        if not reasons:
            reasons.append("No duplicate content detected")

        return {
            'score': round(score, 1),
            'explanation': '; '.join(reasons),
        }

    @staticmethod
    def calculate_ai_like_score(text):
        score = 0
        reasons = []
        text_lower = text.lower()

        structured_markers = [
            r'\bfirst(?:ly| of all)\b', r'\bsecond(?:ly)\b', r'\bthird(?:ly)\b',
            r'\bin conclusion\b', r'\bto summarize\b', r'\bin summary\b',
            r'\bmoreover\b', r'\bfurthermore\b', r'\badditionally\b',
            r'\bconsequently\b', r'\bnevertheless\b', r'\bnonetheless\b',
            r'\bon the other hand\b', r'\bas a result\b', r'\bfor example\b',
            r'\bfor instance\b', r'\bin other words\b',
        ]
        marker_count = sum(1 for p in structured_markers if re.search(p, text_lower))
        if marker_count > 1:
            score += marker_count * 10
            reasons.append(f"Uses {marker_count} structured transition(s)")

        if len(text) > 100:
            sentences = re.split(r'[.!?]+', text)
            avg_sentence_len = len(text.split()) / max(len(sentences), 1)
            if avg_sentence_len > 20:
                score += 15
                reasons.append("Unusually long average sentence length")

        hedging = ['might', 'could', 'perhaps', 'possibly', 'may', 'seems',
                   'appears', 'tends to', 'in general', 'overall']
        hedge_count = sum(1 for h in hedging if h in text_lower.split())
        if hedge_count > 2:
            score += hedge_count * 5
            reasons.append(f"Uses {hedge_count} hedging word(s)")

        bullet_like = ['1)', '2)', '3)', 'first -', 'second -', '- first', '- second']
        if any(b in text_lower for b in bullet_like):
            score += 15
            reasons.append("List-like structure detected")

        word_count = len(text.split())
        if word_count > 50:
            repeats = {}
            for w in text_lower.split():
                repeats[w] = repeats.get(w, 0) + 1
            max_repeat = max(repeats.values())
            if max_repeat > word_count * 0.15:
                score += 10
                reasons.append("Word repetition patterns detected")

        score = min(score, 100)

        if score > 0:
            reasons.insert(0, "Possible AI-generated writing indicators detected.")

        if not reasons:
            reasons.append("No AI-like writing patterns detected")

        return {
            'score': round(score, 1),
            'explanation': '; '.join(reasons),
        }

    @staticmethod
    def calculate_bot_score(text, all_comments):
        score = 0
        reasons = []

        if len(text.split()) < 3:
            score += 10
            reasons.append("Very short comment")

        same_count = sum(1 for c in all_comments if c.lower().strip() == text.lower().strip())
        if same_count > 1:
            score += same_count * 20
            reasons.append(f"Comment posted {same_count} times")

        link_count = len(re.findall(r'https?://\S+', text))
        if link_count > 0:
            score += link_count * 15
            reasons.append("Contains links")

        numeric_patterns = re.findall(r'\d{5,}', text)
        if numeric_patterns:
            score += 15
            reasons.append("Contains long numeric sequences")

        score = min(score, 100)

        if not reasons:
            reasons.append("No bot-like behavior detected")

        return {
            'score': round(score, 1),
            'explanation': '; '.join(reasons),
        }

    @staticmethod
    def calculate_risk_score(spam, toxicity, sentiment_score, duplicate, ai_like, bot):
        spam_weight = 0.20
        toxicity_weight = 0.25
        sentiment_weight = 0.10
        duplicate_weight = 0.10
        ai_like_weight = 0.15
        bot_weight = 0.20

        normalized_sentiment = abs(sentiment_score - 50) * 2

        risk = (
            spam * spam_weight +
            toxicity * toxicity_weight +
            normalized_sentiment * sentiment_weight +
            duplicate * duplicate_weight +
            ai_like * ai_like_weight +
            bot * bot_weight
        )

        risk = round(min(100, max(0, risk)), 1)

        if risk <= 25:
            level = 'Low'
            explanation = 'This comment appears to be genuine and low-risk.'
        elif risk <= 50:
            level = 'Medium'
            explanation = 'This comment shows some indicators that may warrant attention.'
        elif risk <= 75:
            level = 'High'
            explanation = 'This comment has multiple significant risk indicators.'
        else:
            level = 'Critical'
            explanation = 'This comment shows strong indicators of problematic content.'

        return {
            'score': risk,
            'level': level,
            'explanation': explanation,
        }
