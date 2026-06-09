import re
from collections import Counter


STOPWORDS = {
    'a', 'an', 'the', 'is', 'it', 'in', 'on', 'at', 'to', 'for', 'of', 'by',
    'with', 'as', 'and', 'or', 'but', 'not', 'no', 'so', 'if', 'be', 'are',
    'was', 'were', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'can', 'could', 'shall', 'should', 'may', 'might', 'must',
    'i', 'you', 'he', 'she', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'its', 'our', 'their', 'this', 'that', 'these', 'those',
    'what', 'which', 'who', 'whom', 'when', 'where', 'why', 'how', 'all', 'each',
    'every', 'both', 'few', 'more', 'most', 'some', 'any', 'no', 'only', 'very',
    'just', 'also', 'too', 'up', 'down', 'out', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'than', 'into',
}


class TranscriptProcessingService:

    @staticmethod
    def clean_text(text):
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def extract_keywords(text, top_n=20):
        cleaned = TranscriptProcessingService.clean_text(text)
        tokens = [w for w in cleaned.split() if w not in STOPWORDS and len(w) > 2]
        counter = Counter(tokens)
        return counter.most_common(top_n)

    @staticmethod
    def extract_phrases(text, min_length=2, max_length=4):
        cleaned = TranscriptProcessingService.clean_text(text)
        tokens = cleaned.split()
        phrases = []
        for n in range(min_length, max_length + 1):
            for i in range(len(tokens) - n + 1):
                phrase = ' '.join(tokens[i:i + n])
                if all(w not in STOPWORDS or len(w) > 3 for w in tokens[i:i + n]):
                    phrases.append(phrase)
        counter = Counter(phrases)
        return counter.most_common(20)

    @staticmethod
    def get_topics(segments, top_n=5):
        all_text = ' '.join(s if isinstance(s, str) else s.get('text', '') if isinstance(s, dict) else s.text for s in segments)
        keywords = TranscriptProcessingService.extract_keywords(all_text, top_n * 4)
        seen = set()
        topics = []
        for word, count in keywords:
            if word not in seen and len(word) > 3:
                topics.append(word)
                seen.add(word)
                if len(topics) >= top_n:
                    break
        return topics
