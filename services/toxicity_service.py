import re


class ToxicityService:
    PROFANITY_PATTERNS = [
        re.compile(r'\b(fuck|fck|f\*ck|fu+k)\b', re.IGNORECASE),
        re.compile(r'\b(sh[i1][t7]|sh!t)\b', re.IGNORECASE),
        re.compile(r'\b(ass|a$$|a55)\b', re.IGNORECASE),
        re.compile(r'\b(damn|dammit)\b', re.IGNORECASE),
        re.compile(r'\b(b[i1][t7]ch|b!tch)\b', re.IGNORECASE),
        re.compile(r'\b(bastard)\b', re.IGNORECASE),
        re.compile(r'\b(crap)\b', re.IGNORECASE),
        re.compile(r'\b(dick|cock)\b', re.IGNORECASE),
        re.compile(r'\b(piss)\b', re.IGNORECASE),
    ]

    INSULT_PATTERNS = [
        re.compile(r'\b( stupid | idiot | moron | imbecile | retard )', re.IGNORECASE),
        re.compile(r'\b(dumb|loser|jerk|idiot|fool)\b', re.IGNORECASE),
        re.compile(r'\b(worthless|ignorant|clueless)\b', re.IGNORECASE),
        re.compile(r'\b(get\s+(lost|out))', re.IGNORECASE),
        re.compile(r'\b(shut\s+up)\b', re.IGNORECASE),
    ]

    THREAT_PATTERNS = [
        re.compile(r'\b(kill|murder|hurt|attack|destroy)\b', re.IGNORECASE),
        re.compile(r'\b(i\'?ll\s+(get|find|hurt|kill))\b', re.IGNORECASE),
        re.compile(r'\b(you\s+(should\s+)?(be\s+)?(scared|afraid))\b', re.IGNORECASE),
        re.compile(r'\b(watch\s+(your\s+)?back)\b', re.IGNORECASE),
        re.compile(r'\b(die|death|dead)\b', re.IGNORECASE),
    ]

    HARASSMENT_PATTERNS = [
        re.compile(r'\b(u\s+(suck|sux))\b', re.IGNORECASE),
        re.compile(r'\b(go\s+(away|to\s+hell|crawl))\b', re.IGNORECASE),
        re.compile(r'\b(leave\s+(me|us)\s+alone)\b', re.IGNORECASE),
        re.compile(r'\b(stop\s+posting)\b', re.IGNORECASE),
        re.compile(r'\b(nobody\s+(likes|loves|wants))\b', re.IGNORECASE),
    ]

    HATE_LANGUAGE_PATTERNS = [
        re.compile(r'\b(racial|racist|sexist|homophobic|bigot)\b', re.IGNORECASE),
        re.compile(r'\b(supremacist|nazi|fascist)\b', re.IGNORECASE),
    ]

    AGGRESSIVE_PATTERNS = [
        re.compile(r'[A-Z]{4,}'),
        re.compile(r'!{3,}'),
        re.compile(r'\?{3,}'),
        re.compile(r'[A-Z][a-z]+[A-Z][a-z]+[A-Z]'),
    ]

    @classmethod
    def analyze(cls, text):
        if not text or not text.strip():
            return {
                'toxicity_score': 0.0,
                'confidence': 0.0,
                'toxicity_label': 'Low',
                'explanation': 'No text to analyze.',
            }

        reasons = []
        severity = 0.0
        total_matches = 0

        profanity_count = sum(1 for p in cls.PROFANITY_PATTERNS if p.search(text))
        if profanity_count > 0:
            severity += profanity_count * 20
            total_matches += profanity_count
            reasons.append(f'Profanity detected ({profanity_count} instance(s))')

        insult_count = sum(1 for p in cls.INSULT_PATTERNS if p.search(text))
        if insult_count > 0:
            severity += insult_count * 18
            total_matches += insult_count
            reasons.append('Insulting language detected')

        threat_count = sum(1 for p in cls.THREAT_PATTERNS if p.search(text))
        if threat_count > 0:
            severity += threat_count * 25
            total_matches += threat_count
            reasons.append('Threatening language detected')

        harass_count = sum(1 for p in cls.HARASSMENT_PATTERNS if p.search(text))
        if harass_count > 0:
            severity += harass_count * 15
            total_matches += harass_count
            reasons.append('Harassment patterns detected')

        hate_count = sum(1 for p in cls.HATE_LANGUAGE_PATTERNS if p.search(text))
        if hate_count > 0:
            severity += hate_count * 30
            total_matches += hate_count
            reasons.append('Hate speech indicators detected')

        aggressive_count = sum(1 for p in cls.AGGRESSIVE_PATTERNS if p.search(text))
        if aggressive_count > 0:
            severity += aggressive_count * 10
            total_matches += aggressive_count
            reasons.append('Aggressive writing style detected')

        toxicity_score = min(100.0, severity)

        if toxicity_score <= 15:
            label = 'Low'
            explanation = 'No significant toxic content detected.'
        elif toxicity_score <= 40:
            label = 'Medium'
            explanation = 'Mild toxic language detected. May require attention.'
        elif toxicity_score <= 70:
            label = 'High'
            explanation = 'Significant toxic language detected. Review recommended.'
        else:
            label = 'Critical'
            explanation = 'Severe toxic content detected. Immediate review recommended.'

        if reasons:
            explanation = '; '.join(reasons) + '. ' + explanation

        confidence = min(0.95, 0.4 + (toxicity_score / 100.0) * 0.55)

        return {
            'toxicity_score': round(toxicity_score, 1),
            'confidence': round(confidence, 2),
            'toxicity_label': label,
            'explanation': explanation,
        }
