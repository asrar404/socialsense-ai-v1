from datetime import datetime, timezone
from flask import current_app
from database import db
from models.video_transcript import VideoTranscript
from models.transcript_segment import TranscriptSegment


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


LANGUAGE_FALLBACKS = [
    ['en'],
    ['en-US'],
    ['en-GB'],
    ['en-IN'],
    ['hi'],
]


class TranscriptService:

    SOURCE_YOUTUBE = VideoTranscript.SOURCE_YOUTUBE
    SOURCE_TRANSCRIPT_API = VideoTranscript.SOURCE_TRANSCRIPT_API
    SOURCE_MANUAL = VideoTranscript.SOURCE_MANUAL
    SOURCE_DEMO = VideoTranscript.SOURCE_DEMO
    SOURCE_FALLBACK_GENERATED = VideoTranscript.SOURCE_FALLBACK_GENERATED
    SOURCE_UNAVAILABLE = VideoTranscript.SOURCE_UNAVAILABLE

    def fetch_and_store(self, youtube_analysis_id, video_id, language='en'):
        existing = VideoTranscript.query.filter_by(youtube_analysis_id=youtube_analysis_id).first()
        if existing:
            return existing

        if not current_app.config.get('ENABLE_TRANSCRIPT_ANALYSIS', True):
            return self._mark_unavailable(youtube_analysis_id, video_id, reason=VideoTranscript.FAILURE_NONE)

        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            api = YouTubeTranscriptApi()

            language_list = self._build_language_list(language)
            last_error = None

            for lang_group in language_list:
                try:
                    lang_args = {'languages': lang_group} if lang_group else {}
                    fetched = api.fetch(video_id, **lang_args)
                    segments_data = [
                        {'text': s.text, 'start': s.start, 'end': s.start + s.duration}
                        for s in fetched.snippets
                    ]
                    return self._store_transcript(youtube_analysis_id, video_id, segments_data,
                                                  self.SOURCE_TRANSCRIPT_API, fetched.language_code or language,
                                                  fetched.is_generated)
                except Exception as e:
                    last_error = e
                    current_app.logger.debug(f'Transcript lang={lang_group} failed for {video_id}: {e}')

            if last_error:
                reason = self._classify_error(last_error, video_id)
                return self._mark_unavailable(youtube_analysis_id, video_id, reason=reason)

        except ImportError:
            current_app.logger.warning('youtube_transcript_api not installed')
            return self._mark_unavailable(youtube_analysis_id, video_id,
                                          reason=VideoTranscript.FAILURE_API_ERROR)

        return self._mark_unavailable(youtube_analysis_id, video_id,
                                      reason=VideoTranscript.FAILURE_UNKNOWN)

    def store_fallback_generated(self, youtube_analysis_id, video_id, title='', description='', comments=None):
        existing = VideoTranscript.query.filter_by(youtube_analysis_id=youtube_analysis_id).first()
        if existing and existing.is_available:
            return existing

        parts = []
        if title:
            parts.append(title)
        if description:
            parts.append(description)
        if comments:
            comment_texts = [c if isinstance(c, str) else c.get('text', '') for c in comments]
            parts.extend(comment_texts[:10])

        if not parts:
            return self._mark_unavailable(youtube_analysis_id, video_id,
                                          reason=VideoTranscript.FAILURE_NO_TRANSCRIPT)

        full_text = ' '.join(parts)
        sentences = full_text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if not sentences:
            return self._mark_unavailable(youtube_analysis_id, video_id,
                                          reason=VideoTranscript.FAILURE_NO_TRANSCRIPT)

        segment_duration = 5.0
        segments_data = []
        for i, sentence in enumerate(sentences):
            segments_data.append({
                'text': sentence,
                'start': i * segment_duration,
                'end': (i + 1) * segment_duration,
            })

        return self._store_transcript(youtube_analysis_id, video_id, segments_data,
                                      self.SOURCE_FALLBACK_GENERATED, 'en', True)

    def store_demo_transcript(self, youtube_analysis_id, video_id):
        demo_segments = [
            {'start': 0.0, 'end': 4.0, 'text': 'Welcome to this video where we explore the latest technology trends.'},
            {'start': 4.0, 'end': 8.5, 'text': 'Today we are reviewing a brand new product that has generated a lot of discussion.'},
            {'start': 8.5, 'end': 13.0, 'text': 'The product features an innovative design with high quality materials.'},
            {'start': 13.0, 'end': 18.0, 'text': 'Many users have reported positive experiences with the battery life.'},
            {'start': 18.0, 'end': 23.5, 'text': 'However there are some concerns about the pricing strategy.'},
            {'start': 23.5, 'end': 28.0, 'text': 'The customer support team has been responsive to feedback.'},
            {'start': 28.0, 'end': 33.0, 'text': 'Overall this product represents a significant step forward in the industry.'},
            {'start': 33.0, 'end': 38.0, 'text': 'We recommend watching the full review for more detailed analysis.'},
        ]
        return self._store_transcript(youtube_analysis_id, video_id, demo_segments,
                                      self.SOURCE_DEMO, 'en', False)

    def get_by_youtube_analysis_id(self, youtube_analysis_id):
        return VideoTranscript.query.filter_by(youtube_analysis_id=youtube_analysis_id).first()

    def get_segments(self, transcript_id):
        return TranscriptSegment.query.filter_by(transcript_id=transcript_id).order_by(TranscriptSegment.segment_index).all()

    def get_full_text(self, transcript_id):
        segments = self.get_segments(transcript_id)
        return ' '.join(s.text for s in segments)

    def get_all_video_transcripts(self):
        return VideoTranscript.query.order_by(VideoTranscript.created_at.desc()).all()

    def delete_transcript(self, transcript_id):
        transcript = VideoTranscript.query.get(transcript_id)
        if transcript:
            db.session.delete(transcript)
            db.session.commit()
            return True
        return False

    def _build_language_list(self, preferred_language):
        seen = set()
        language_list = []

        if preferred_language and preferred_language not in seen:
            language_list.append([preferred_language])
            seen.add(preferred_language)

        for group in LANGUAGE_FALLBACKS:
            key = tuple(group)
            if key not in seen:
                language_list.append(group)
                seen.add(key)

        language_list.append(None)
        return language_list

    def _classify_error(self, error, video_id):
        error_str = str(error).lower()
        if 'block' in error_str or '429' in error_str:
            return VideoTranscript.FAILURE_IP_BLOCKED
        if 'disabled' in error_str or 'caption' in error_str:
            return VideoTranscript.FAILURE_CAPTIONS_DISABLED
        if 'no transcript' in error_str:
            return VideoTranscript.FAILURE_NO_TRANSCRIPT
        if 'language' in error_str or 'lang' in error_str:
            return VideoTranscript.FAILURE_UNSUPPORTED_LANGUAGE
        if 'video_id' in error_str:
            return VideoTranscript.FAILURE_NO_TRANSCRIPT
        return VideoTranscript.FAILURE_API_ERROR

    def _store_transcript(self, youtube_analysis_id, video_id, segments_data, source, language, is_auto):
        full_text = ' '.join(s['text'] for s in segments_data)
        word_count = len(full_text.split())
        duration_seconds = segments_data[-1]['end'] - segments_data[0]['start'] if segments_data else 0.0

        transcript = VideoTranscript(
            youtube_analysis_id=youtube_analysis_id,
            video_id=video_id,
            language=language,
            transcript_text=full_text,
            source=source,
            is_auto_generated=is_auto,
            segment_count=len(segments_data),
            word_count=word_count,
            duration_seconds=round(duration_seconds, 1),
            created_at=_now(),
            updated_at=_now(),
        )
        db.session.add(transcript)
        db.session.flush()

        for i, seg in enumerate(segments_data):
            segment = TranscriptSegment(
                transcript_id=transcript.id,
                start_time=seg['start'],
                end_time=seg['end'],
                text=seg['text'],
                word_count=len(seg['text'].split()),
                segment_index=i,
                created_at=_now(),
            )
            db.session.add(segment)

        db.session.commit()
        return transcript

    def _mark_unavailable(self, youtube_analysis_id, video_id, reason=None):
        transcript = VideoTranscript(
            youtube_analysis_id=youtube_analysis_id,
            video_id=video_id,
            transcript_text=None,
            source=self.SOURCE_UNAVAILABLE,
            segment_count=0,
            word_count=0,
            failure_reason=reason,
            created_at=_now(),
            updated_at=_now(),
        )
        db.session.add(transcript)
        db.session.commit()
        return transcript
