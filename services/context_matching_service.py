import re
import math
import json
from collections import Counter
from services.transcript_processing_service import TranscriptProcessingService, STOPWORDS
from models.comment_context import CommentContext
from database import db


class ContextMatchingService:

    TFIDF_WEIGHT = 0.5
    KEYWORD_WEIGHT = 0.3
    PHRASE_WEIGHT = 0.2

    def __init__(self):
        self.processor = TranscriptProcessingService()

    def compute_context(self, comment_text, transcript_text, segments, top_keywords, top_phrases):
        cleaned_comment = self.processor.clean_text(comment_text)
        if not cleaned_comment:
            return self._default_result()

        if not transcript_text or not segments:
            return self._default_result()

        tfidf_score = self._tfidf_similarity(cleaned_comment, transcript_text)
        keyword_score = self._keyword_overlap(cleaned_comment, top_keywords)
        phrase_score = self._phrase_overlap(cleaned_comment, top_phrases)

        relevance_score = (
            tfidf_score * self.TFIDF_WEIGHT +
            keyword_score * self.KEYWORD_WEIGHT +
            phrase_score * self.PHRASE_WEIGHT
        )

        relevance_score = round(min(max(relevance_score, 0.0), 1.0), 4)

        best_segment, match_detail = self._find_best_segment(cleaned_comment, segments)

        off_topic_score = round(max(0.0, 1.0 - relevance_score), 4)

        topic_alignment = round(self._topic_alignment(cleaned_comment, top_keywords), 4)

        label = self._classify_relevance(relevance_score)

        matched_keywords = [kw for kw, _ in top_keywords
                           if kw in cleaned_comment]
        matched_phrases = []
        for phrase, _ in top_phrases:
            if phrase in cleaned_comment:
                matched_phrases.append(phrase)

        reason = self._generate_reason(label, relevance_score, off_topic_score,
                                        tfidf_score, keyword_score, phrase_score)

        return {
            'transcript_relevance_score': relevance_score,
            'topic_alignment_score': topic_alignment,
            'off_topic_score': off_topic_score,
            'context_match_label': label,
            'matched_keywords': json.dumps(matched_keywords[:10]) if matched_keywords else None,
            'matched_phrases': json.dumps(matched_phrases[:5]) if matched_phrases else None,
            'reason': reason,
            'best_segment_id': best_segment['id'] if best_segment else None,
        }

    def create_comment_context(self, comment_result_id, transcript_id, context_data):
        ctx = CommentContext(
            comment_result_id=comment_result_id,
            transcript_id=transcript_id,
            best_segment_id=context_data.get('best_segment_id'),
            transcript_relevance_score=context_data.get('transcript_relevance_score', 0.0),
            topic_alignment_score=context_data.get('topic_alignment_score', 0.0),
            off_topic_score=context_data.get('off_topic_score', 0.0),
            context_match_label=context_data.get('context_match_label', CommentContext.LABEL_UNKNOWN),
            matched_keywords=context_data.get('matched_keywords'),
            matched_phrases=context_data.get('matched_phrases'),
            reason=context_data.get('reason'),
        )
        db.session.add(ctx)
        db.session.commit()
        return ctx

    def _tfidf_similarity(self, cleaned_comment, transcript_text):
        cleaned_transcript = self.processor.clean_text(transcript_text)
        if not cleaned_transcript:
            return 0.0

        comment_tokens = cleaned_comment.split()
        transcript_tokens = cleaned_transcript.split()

        if not comment_tokens or not transcript_tokens:
            return 0.0

        comment_tf = Counter(comment_tokens)
        transcript_tf = Counter(transcript_tokens)
        total_transcript = len(transcript_tokens)

        idf_comment = {w: math.log((total_transcript + 1) / (transcript_tf.get(w, 0) + 1)) + 1
                       for w in comment_tokens if w not in STOPWORDS}

        dot_product = sum(comment_tf.get(w, 0) * idf_comment.get(w, 0)
                          for w in comment_tokens if w in transcript_tf)
        comment_magnitude = math.sqrt(sum(idf_comment.get(w, 0) ** 2 for w in comment_tokens))

        if comment_magnitude == 0:
            return 0.0

        return min(dot_product / comment_magnitude, 1.0)

    def _keyword_overlap(self, cleaned_comment, top_keywords):
        if not top_keywords:
            return 0.0

        comment_words = set(cleaned_comment.split())
        keywords_set = set(kw for kw, _ in top_keywords)

        if not keywords_set:
            return 0.0

        intersection = comment_words & keywords_set
        return len(intersection) / len(keywords_set)

    def _phrase_overlap(self, cleaned_comment, top_phrases):
        if not top_phrases:
            return 0.0

        matches = 0
        for phrase, _ in top_phrases:
            if phrase in cleaned_comment:
                matches += 1

        return matches / len(top_phrases) if top_phrases else 0.0

    def _find_best_segment(self, cleaned_comment, segments):
        best = None
        best_score = -1
        detail = {}

        for seg in segments:
            seg_text = seg.text if hasattr(seg, 'text') else seg.get('text', '')
            cleaned_seg = self.processor.clean_text(seg_text)

            comment_words = set(cleaned_comment.split())

            if not comment_words or not cleaned_seg:
                continue

            overlap = comment_words & set(cleaned_seg.split())
            score = len(overlap) / max(len(comment_words), 1)

            if score > best_score:
                best_score = score
                seg_id = seg.id if hasattr(seg, 'id') else None
                best = {'id': seg_id, 'text': seg_text,
                        'start_time': seg.start_time if hasattr(seg, 'start_time') else seg.get('start'),
                        'end_time': seg.end_time if hasattr(seg, 'end_time') else seg.get('end')}

        return best, detail

    def _topic_alignment(self, cleaned_comment, top_keywords):
        if not top_keywords:
            return 0.0

        comment_words = set(cleaned_comment.split())
        keywords_set = set(kw for kw, _ in top_keywords)

        if not keywords_set:
            return 1.0

        intersection = comment_words & keywords_set
        return len(intersection) / max(len(keywords_set), 1)

    def _classify_relevance(self, score):
        if score >= 0.7:
            return CommentContext.LABEL_HIGHLY_RELEVANT
        if score >= 0.4:
            return CommentContext.LABEL_RELEVANT
        if score >= 0.2:
            return CommentContext.LABEL_PARTIALLY_RELEVANT
        return CommentContext.LABEL_OFF_TOPIC

    def _generate_reason(self, label, relevance, off_topic, tfidf, keyword_score, phrase_score):
        if label == CommentContext.LABEL_HIGHLY_RELEVANT:
            return 'Comment closely relates to video content'
        if label == CommentContext.LABEL_RELEVANT:
            return 'Comment partially relates to video content'
        if label == CommentContext.LABEL_PARTIALLY_RELEVANT:
            return 'Comment has minimal connection to video content'
        return 'Comment is off-topic from video content'

    def _default_result(self):
        return {
            'transcript_relevance_score': 0.0,
            'topic_alignment_score': 0.0,
            'off_topic_score': 1.0,
            'context_match_label': CommentContext.LABEL_UNKNOWN,
            'matched_keywords': None,
            'matched_phrases': None,
            'reason': 'No transcript available',
            'best_segment_id': None,
        }
