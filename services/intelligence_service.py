from models.comment_result import CommentResult
from collections import Counter
import re


class IntelligenceService:
    STOP_WORDS = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                  'could', 'should', 'may', 'might', 'shall', 'can', 'need',
                  'dare', 'ought', 'used', 'to', 'of', 'in', 'for', 'on',
                  'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
                  'before', 'after', 'above', 'below', 'between', 'out', 'off',
                  'over', 'under', 'again', 'further', 'then', 'once', 'here',
                  'there', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
                  'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                  'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                  'just', 'because', 'but', 'and', 'or', 'if', 'while', 'that',
                  'this', 'these', 'those', 'it', 'its', 'i', 'me', 'my', 'we',
                  'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her', 'they',
                  'them', 'their', 'what', 'which', 'who', 'whom'}

    TOXIC_TERMS = {'stupid', 'idiot', 'hate', 'kill', 'die', 'ugly', 'dumb',
                   'loser', 'trash', 'garbage', 'worthless', 'terrible', 'awful'}

    SPAM_TERMS = {'buy', 'click', 'subscribe', 'free', 'limited', 'offer',
                  'act now', 'don\'t miss', 'hurry', 'exclusive', 'deal',
                  'discount', 'promotion', 'guaranteed', 'click here',
                  'sign up', 'join now', 'check out'}

    RISK_TERMS = {'scam', 'fraud', 'fake', 'illegal', 'steal', 'hack',
                  'password', 'credit card', 'bank', 'account', 'verify',
                  'suspended', 'urgent', 'warning', 'alert'}

    def extract_keywords(self, comments, top_n=10):
        text = ' '.join(c.comment_text for c in comments if c.comment_text)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        words = [w for w in words if w not in self.STOP_WORDS and len(w) > 2]
        return [{'word': w, 'count': c} for w, c in Counter(words).most_common(top_n)]

    def extract_phrases(self, comments, top_n=5):
        phrases = []
        for c in comments:
            if not c.comment_text:
                continue
            words = c.comment_text.lower().split()
            for i in range(len(words) - 1):
                if len(words[i]) > 2 and len(words[i + 1]) > 2:
                    phrases.append(f'{words[i]} {words[i + 1]}')
        return [{'phrase': p, 'count': c} for p, c in Counter(phrases).most_common(top_n)]

    def extract_risk_terms(self, comments):
        found = Counter()
        for c in comments:
            if not c.comment_text:
                continue
            text_lower = c.comment_text.lower()
            for term in self.RISK_TERMS:
                if term in text_lower:
                    found[term] += 1
        return [{'term': t, 'count': c} for t, c in found.most_common(10)]

    def extract_toxic_terms(self, comments):
        found = Counter()
        for c in comments:
            if not c.comment_text:
                continue
            text_lower = c.comment_text.lower()
            for term in self.TOXIC_TERMS:
                if term in text_lower:
                    found[term] += 1
        return [{'term': t, 'count': c} for t, c in found.most_common(10)]

    def extract_spam_indicators(self, comments):
        found = Counter()
        for c in comments:
            if not c.comment_text:
                continue
            text_lower = c.comment_text.lower()
            for term in self.SPAM_TERMS:
                if term in text_lower:
                    found[term] += 1
        return [{'indicator': t, 'count': c} for t, c in found.most_common(10)]

    def analyze_comments(self, comments):
        return {
            'keywords': self.extract_keywords(comments),
            'phrases': self.extract_phrases(comments),
            'risk_terms': self.extract_risk_terms(comments),
            'toxic_terms': self.extract_toxic_terms(comments),
            'spam_indicators': self.extract_spam_indicators(comments),
        }
