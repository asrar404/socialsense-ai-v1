from datetime import datetime, timezone
from flask import current_app
from database import db
from models.analysis import Analysis, YouTubeAnalysis
from models.reddit_analysis import RedditAnalysis
from models.comment_result import CommentResult
from repositories.analysis_repository import AnalysisRepository
from repositories.comment_result_repository import CommentResultRepository
from repositories.reddit_analysis_repository import RedditAnalysisRepository
from services.youtube_service import YouTubeService, YouTubeAPIError
from services.reddit_service import RedditService, RedditAPIError, RedditDemoService
from services.demo_service import DemoService
from services.risk_scoring_service import RiskScoringService
from services.sentiment_service import SentimentService
from services.toxicity_service import ToxicityService
from services.spam_service import SpamService
from services.bot_detection_service import BotDetectionService
from services.risk_engine import RiskEngine
from services.transcript_service import TranscriptService
from services.transcript_processing_service import TranscriptProcessingService
from services.context_matching_service import ContextMatchingService
from models.video_transcript import VideoTranscript
from models.comment_context import CommentContext


class AnalysisService:
    def __init__(self):
        self.analysis_repo = AnalysisRepository()
        self.comment_repo = CommentResultRepository()
        self.reddit_repo = RedditAnalysisRepository()
        self.youtube_service = YouTubeService()
        self.reddit_service = RedditService()
        self.reddit_demo = RedditDemoService()
        self.demo_service = DemoService()
        self.risk_scorer = RiskScoringService()
        self.transcript_service = TranscriptService()
        self.transcript_processor = TranscriptProcessingService()
        self.context_matcher = ContextMatchingService()

    def create_youtube_analysis(self, user_id, video_url, comment_limit=100):
        video_id = self.youtube_service.extract_video_id(video_url)
        if not video_id:
            return {'success': False, 'error': 'Invalid YouTube URL or Video ID.'}

        api_key = current_app.config.get('YOUTUBE_API_KEY', '')
        is_demo = not api_key

        video_info = None
        comments = []
        api_error = None

        if not is_demo:
            try:
                video_info = self.youtube_service.fetch_video_info(video_id)
                comments = self.youtube_service.fetch_comments(video_id, max_results=comment_limit)
            except YouTubeAPIError as e:
                api_error = e.error_type
                flash_message = str(e)
                return {'success': False, 'error': flash_message, 'api_error': e.error_type}
        else:
            video_info = self.demo_service.get_video_info_by_id(video_id)
            comments = self.demo_service.get_comments()

        if not video_info:
            video_info = {
                'video_id': video_id,
                'title': f'Video ({video_id})',
                'description': '',
                'channel': 'Unknown',
                'published_at': None,
                'view_count': 0,
                'like_count': 0,
                'comment_count': 0,
            }

        if not comments:
            comments = []

        analysis = self.analysis_repo.create(user_id=user_id, analysis_type='youtube')

        yt_analysis = YouTubeAnalysis(
            analysis_id=analysis.id,
            video_id=video_info['video_id'],
            video_title=video_info.get('title', 'Unknown Title'),
            video_description=video_info.get('description', ''),
            channel_name=video_info.get('channel', 'Unknown'),
            published_at=video_info.get('published_at'),
            view_count=video_info.get('view_count', 0),
            like_count=video_info.get('like_count', 0),
            comment_count=len(comments),
            comment_limit=comment_limit,
            is_demo=is_demo,
            api_error=api_error,
        )
        db.session.add(yt_analysis)
        db.session.commit()

        all_texts = [c['text'] for c in comments]
        for comment in comments:
            self._analyze_and_store_comment_v2(analysis.id, comment, all_texts)

        self._generate_analysis_summary(analysis.id)

        transcript_obj = None
        if current_app.config.get('ENABLE_TRANSCRIPT_ANALYSIS', True):
            try:
                if is_demo:
                    transcript_obj = self.transcript_service.store_demo_transcript(yt_analysis.id, video_id)
                else:
                    lang = current_app.config.get('TRANSCRIPT_LANGUAGE_PRIORITY', 'en')
                    transcript_obj = self.transcript_service.fetch_and_store(yt_analysis.id, video_id, language=lang)

                if transcript_obj and not transcript_obj.is_available and current_app.config.get('ENABLE_TRANSCRIPT_FALLBACK_DEMO', False):
                    fallback_comments = comments if not is_demo else None
                    transcript_obj = self.transcript_service.store_fallback_generated(
                        yt_analysis.id, video_id,
                        title=video_info.get('title', ''),
                        description=video_info.get('description', ''),
                        comments=fallback_comments,
                    )

                if transcript_obj and transcript_obj.is_available:
                    top_keywords = self.transcript_processor.extract_keywords(transcript_obj.transcript_text or '', 20)
                    top_phrases = self.transcript_processor.extract_phrases(transcript_obj.transcript_text or '', 2, 4)
                    segments = self.transcript_service.get_segments(transcript_obj.id)

                    transcript_obj.topics = ', '.join(self.transcript_processor.get_topics(
                        [seg.text for seg in segments], 5))
                    transcript_obj.summary = self._generate_transcript_summary(transcript_obj.transcript_text or '')

                    comment_results = self.comment_repo.get_by_analysis_id(analysis.id)
                    for cr in comment_results:
                        context_data = self.context_matcher.compute_context(
                            cr.comment_text,
                            transcript_obj.transcript_text or '',
                            segments,
                            top_keywords,
                            top_phrases,
                        )
                        self.context_matcher.create_comment_context(cr.id, transcript_obj.id, context_data)

                    transcript_obj.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    db.session.commit()
            except Exception as e:
                current_app.logger.warning(f'Transcript processing failed: {e}')

        return {
            'success': True,
            'analysis_id': analysis.id,
            'is_demo': is_demo,
            'comment_count': len(comments),
            'transcript_available': bool(transcript_obj and transcript_obj.is_available),
        }

    def create_reddit_analysis(self, user_id, post_id, subreddit=None, input_type='post', comment_limit=100):
        has_creds = bool(current_app.config.get('REDDIT_CLIENT_ID', '') and current_app.config.get('REDDIT_CLIENT_SECRET', ''))
        is_demo = not has_creds

        if not is_demo:
            try:
                post_info = self.reddit_service.fetch_post_info(post_id)
                comments = self.reddit_service.fetch_comments(post_id, max_results=comment_limit)
            except RedditAPIError as e:
                return {'success': False, 'error': str(e), 'api_error': e.error_type}
        else:
            post_info = self.reddit_demo.get_post_info(post_id, subreddit)
            comments = self.reddit_demo.get_comments()

        if not comments:
            comments = []

        analysis = self.analysis_repo.create(user_id=user_id, analysis_type='reddit')

        reddit = RedditAnalysis(
            analysis_id=analysis.id,
            post_id=post_info['post_id'],
            subreddit=post_info.get('subreddit', ''),
            post_title=post_info.get('title', 'Unknown Post'),
            post_body=post_info.get('body', ''),
            post_author=post_info.get('author', '[deleted]'),
            post_score=post_info.get('score', 0),
            upvote_ratio=post_info.get('upvote_ratio', 0.0),
            comment_count=len(comments),
            comment_limit=comment_limit,
            permalink=post_info.get('permalink', ''),
            created_utc=post_info.get('created_utc'),
            is_demo=is_demo,
        )
        db.session.add(reddit)
        db.session.commit()

        all_texts = [c['text'] for c in comments]
        for comment in comments:
            self._analyze_and_store_comment_v2(analysis.id, comment, all_texts)

        self._generate_analysis_summary(analysis.id)

        return {
            'success': True,
            'analysis_id': analysis.id,
            'is_demo': is_demo,
            'comment_count': len(comments),
        }

    def _analyze_and_store_comment_v2(self, analysis_id, comment, all_texts):
        text = comment['text']

        sentiment = SentimentService.analyze(text)
        toxicity = ToxicityService.analyze(text)
        spam = SpamService.analyze(text, all_texts)
        bot = BotDetectionService.analyze(text, all_texts)
        duplicate = self.risk_scorer.calculate_duplicate_score(text, all_texts)
        risk = RiskEngine.calculate(sentiment, toxicity, spam, bot, duplicate['score'])

        result = CommentResult(
            analysis_id=analysis_id,
            comment_text=text,
            author=comment.get('author', 'Unknown'),
            published_at=comment.get('published_at'),
            spam_score=spam['spam_score'],
            spam_explanation=spam['explanation'],
            spam_confidence=spam['confidence'],
            toxicity_score=toxicity['toxicity_score'],
            toxicity_explanation=toxicity['explanation'],
            toxicity_confidence=toxicity['confidence'],
            sentiment=sentiment['label'],
            sentiment_score=sentiment['score'],
            sentiment_explanation=sentiment['explanation'],
            sentiment_confidence=sentiment['confidence'],
            duplicate_score=duplicate['score'],
            duplicate_explanation=duplicate['explanation'],
            ai_like_score=bot['bot_score'],
            ai_like_explanation=bot['explanation'],
            bot_score=bot['bot_score'],
            bot_explanation=bot['explanation'],
            bot_confidence=bot['confidence'],
            risk_score=risk['final_risk_score'],
            risk_level=risk['final_risk_label'],
            risk_explanation='; '.join(risk['reasons']),
            recommendation=risk['recommendation'],
        )
        db.session.add(result)
        db.session.commit()

    def _generate_analysis_summary(self, analysis_id):
        comments = self.comment_repo.get_by_analysis_id(analysis_id)
        if not comments:
            return

        total = len(comments)
        sentiments = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
        toxicity_levels = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        spam_levels = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        risk_levels = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        total_sentiment = 0.0
        total_toxicity = 0.0
        total_spam = 0.0
        total_bot = 0.0
        critical_count = 0
        concerns = set()

        for c in comments:
            sentiments[c.sentiment or 'Neutral'] = sentiments.get(c.sentiment, 0) + 1
            total_sentiment += c.sentiment_score or 50.0
            total_toxicity += c.toxicity_score or 0.0
            total_spam += c.spam_score or 0.0
            total_bot += c.bot_score or 0.0

            if c.risk_level == 'Critical':
                critical_count += 1
            if c.risk_level:
                risk_levels[c.risk_level] = risk_levels.get(c.risk_level, 0) + 1

            if c.toxicity_score and c.toxicity_score >= 40:
                concerns.add('Toxic language')
            if c.spam_score and c.spam_score >= 40:
                concerns.add('Spam content')
            if c.bot_score and c.bot_score >= 40:
                concerns.add('Automated content')
            if c.duplicate_score and c.duplicate_score >= 40:
                concerns.add('Duplicate posting')

        avg_sentiment = round(total_sentiment / total, 1) if total else 50.0
        avg_toxicity = round(total_toxicity / total, 1) if total else 0.0
        avg_spam = round(total_spam / total, 1) if total else 0.0
        avg_bot = round(total_bot / total, 1) if total else 0.0

        sentiment_pct = {
            k: round(v / total * 100, 1) if total else 0.0
            for k, v in sentiments.items()
        }

        overall_risk = 'Low'
        avg_risk_score = (avg_toxicity * 0.35 + avg_spam * 0.25 + avg_bot * 0.20 + abs(avg_sentiment - 50) * 0.10)
        if avg_risk_score > 25:
            overall_risk = 'Medium'
        if avg_risk_score > 50:
            overall_risk = 'High'
        if avg_risk_score > 75:
            overall_risk = 'Critical'

        summary_parts = [
            f"Comments analyzed: {total}",
            f"Positive: {sentiment_pct.get('Positive', 0)}%",
            f"Neutral: {sentiment_pct.get('Neutral', 0)}%",
            f"Negative: {sentiment_pct.get('Negative', 0)}%",
            f"Average Toxicity: {avg_toxicity}%",
            f"High Risk Comments: {critical_count}",
            f"Overall Community Health: {overall_risk} Risk",
        ]

        if concerns:
            summary_parts.append("Key Concerns:")
            for concern in sorted(concerns):
                summary_parts.append(f"- {concern}")

        summary = '\n'.join(summary_parts)

        analysis = self.analysis_repo.get_by_id(analysis_id)
        if analysis:
            analysis.average_sentiment = avg_sentiment
            analysis.average_toxicity = avg_toxicity
            analysis.average_spam = avg_spam
            analysis.average_bot_score = avg_bot
            analysis.critical_comments_count = critical_count
            analysis.analysis_summary = summary
            db.session.commit()

    def _analyze_and_store_comment(self, analysis_id, comment, all_texts):
        text = comment['text']

        spam = self.risk_scorer.calculate_spam_score(text)
        toxicity = self.risk_scorer.calculate_toxicity_score(text)
        sentiment = self.risk_scorer.calculate_sentiment(text)
        duplicate = self.risk_scorer.calculate_duplicate_score(text, all_texts)
        ai_like = self.risk_scorer.calculate_ai_like_score(text)
        bot = self.risk_scorer.calculate_bot_score(text, all_texts)
        risk = self.risk_scorer.calculate_risk_score(
            spam['score'], toxicity['score'], sentiment['score'],
            duplicate['score'], ai_like['score'], bot['score']
        )

        result = CommentResult(
            analysis_id=analysis_id,
            comment_text=text,
            author=comment.get('author', 'Unknown'),
            published_at=comment.get('published_at'),
            spam_score=spam['score'],
            spam_explanation=spam['explanation'],
            toxicity_score=toxicity['score'],
            toxicity_explanation=toxicity['explanation'],
            sentiment=sentiment['label'],
            sentiment_score=sentiment['score'],
            sentiment_explanation=sentiment['explanation'],
            duplicate_score=duplicate['score'],
            duplicate_explanation=duplicate['explanation'],
            ai_like_score=ai_like['score'],
            ai_like_explanation=ai_like['explanation'],
            bot_score=bot['score'],
            bot_explanation=bot['explanation'],
            risk_score=risk['score'],
            risk_level=risk['level'],
            risk_explanation=risk['explanation'],
        )
        db.session.add(result)
        db.session.commit()

    def get_analysis_results(self, analysis_id, user_id):
        analysis = self.analysis_repo.get_user_analysis_with_reddit(analysis_id, user_id)
        if not analysis:
            return None

        comments = self.comment_repo.get_by_analysis_id(analysis_id)
        high_risk = self.comment_repo.get_high_risk_by_analysis(analysis_id)
        top_spam = self.comment_repo.get_top_spam_by_analysis(analysis_id, limit=5)
        top_toxic = self.comment_repo.get_top_toxic_by_analysis(analysis_id, limit=5)
        sentiment_dist = self.comment_repo.get_sentiment_distribution(analysis_id)
        risk_dist = self.comment_repo.get_risk_distribution(analysis_id)
        averages = self.comment_repo.get_average_scores_by_analysis(analysis_id)

        youtube = analysis.youtube_analysis
        reddit = analysis.reddit_analysis

        transcript = None
        context_distribution = None
        if youtube and youtube.transcript:
            transcript = youtube.transcript
            context_distribution = self.comment_repo.get_context_distribution(analysis_id)

        result = {
            'analysis': analysis,
            'comments': comments,
            'high_risk': high_risk,
            'top_spam': top_spam,
            'top_toxic': top_toxic,
            'sentiment_distribution': sentiment_dist,
            'risk_distribution': risk_dist,
            'averages': averages,
            'comment_count': len(comments),
            'transcript': transcript,
            'context_distribution': context_distribution,
        }

        if analysis.analysis_type == 'reddit' and reddit:
            result['reddit'] = reddit
            result['is_demo'] = reddit.is_demo
            result['api_error'] = reddit.api_error
            result['youtube'] = None
        elif youtube:
            result['youtube'] = youtube
            result['is_demo'] = youtube.is_demo
            result['api_error'] = youtube.api_error
            result['reddit'] = None
        else:
            return None

        return result

    def get_recent_user_analyses(self, user_id, limit=10):
        return self.analysis_repo.get_recent_by_user(user_id, limit)

    def get_dashboard_stats(self, user_id, platform='all'):
        analyses = self.analysis_repo.get_by_user_id(user_id)
        if platform != 'all':
            analyses = [a for a in analyses if a.analysis_type == platform]
        total_analyses = len(analyses)
        total_comments = 0
        total_spam = 0
        total_toxicity = 0
        total_sentiment = 0
        total_ai = 0
        total_risk = 0
        total_bot = 0
        analysis_count = 0
        critical_count = 0
        transcript_count = 0

        for analysis in analyses:
            averages = self.comment_repo.get_average_scores_by_analysis(analysis.id)
            comment_count = self.comment_repo.count_by_analysis(analysis.id)
            total_comments += comment_count
            critical_count += analysis.critical_comments_count or 0
            if comment_count > 0:
                total_spam += averages['avg_spam']
                total_toxicity += averages['avg_toxicity']
                total_sentiment += averages['avg_sentiment']
                total_ai += averages['avg_ai_like']
                total_risk += averages['avg_risk']
                total_bot += averages.get('avg_bot', 0)
                analysis_count += 1
            yt = analysis.youtube_analysis
            if yt and yt.transcript:
                transcript_count += 1

        community_health = 'Low'
        avg_all_risk = total_risk / max(analysis_count, 1)
        if avg_all_risk > 25:
            community_health = 'Medium'
        if avg_all_risk > 50:
            community_health = 'High'
        if avg_all_risk > 75:
            community_health = 'Critical'

        return {
            'total_analyses': total_analyses,
            'total_comments': total_comments,
            'avg_spam': round(total_spam / max(analysis_count, 1), 1),
            'avg_toxicity': round(total_toxicity / max(analysis_count, 1), 1),
            'avg_sentiment': round(total_sentiment / max(analysis_count, 1), 1),
            'avg_ai_like': round(total_ai / max(analysis_count, 1), 1),
            'avg_bot': round(total_bot / max(analysis_count, 1), 1),
            'avg_risk': round(total_risk / max(analysis_count, 1), 1),
            'critical_comments': critical_count,
            'community_health': community_health,
            'transcript_count': transcript_count,
        }

    def get_all_user_analyses_with_data(self, user_id, limit=None):
        analyses = self.analysis_repo.get_by_user_id(user_id)
        if limit:
            analyses = analyses[:limit]
        results = []
        for a in analyses:
            averages = self.comment_repo.get_average_scores_by_analysis(a.id)
            comment_count = self.comment_repo.count_by_analysis(a.id)
            yt = a.youtube_analysis
            reddit = a.reddit_analysis
            if a.analysis_type == 'reddit' and reddit:
                title = reddit.post_title or 'N/A'
                identifier = reddit.post_id
                is_demo = reddit.is_demo
                platform = 'reddit'
            elif yt:
                title = yt.video_title or 'N/A'
                identifier = yt.video_id
                is_demo = yt.is_demo
                platform = 'youtube'
            else:
                title = 'N/A'
                identifier = 'N/A'
                is_demo = False
                platform = 'unknown'
            has_transcript = bool(yt and yt.transcript) if platform == 'youtube' else False
            results.append({
                'id': a.id,
                'title': title,
                'identifier': identifier,
                'platform': platform,
                'comment_count': comment_count,
                'avg_risk': averages['avg_risk'],
                'is_demo': is_demo,
                'has_transcript': has_transcript,
                'created_at': a.created_at,
            })
        return results

    def _generate_transcript_summary(self, transcript_text):
        if not transcript_text:
            return None
        words = transcript_text.split()
        word_count = len(words)
        if word_count <= 100:
            return transcript_text
        sentences = transcript_text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        key_sentences = sentences[:5]
        summary = '. '.join(key_sentences)
        if not summary.endswith('.'):
            summary += '.'
        return summary
