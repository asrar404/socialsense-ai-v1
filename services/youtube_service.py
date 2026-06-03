import re
import traceback
from datetime import datetime, timezone
from flask import current_app


class YouTubeAPIError(Exception):
    def __init__(self, message, error_type='api_error'):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


class VideoNotFoundError(YouTubeAPIError):
    def __init__(self, message='Video not found.'):
        super().__init__(message, 'video_not_found')


class CommentsDisabledError(YouTubeAPIError):
    def __init__(self, message='Comments are disabled for this video.'):
        super().__init__(message, 'comments_disabled')


class QuotaExceededError(YouTubeAPIError):
    def __init__(self, message='YouTube API quota exceeded. Try again later.'):
        super().__init__(message, 'quota_exceeded')


class NetworkError(YouTubeAPIError):
    def __init__(self, message='Network error contacting YouTube API.'):
        super().__init__(message, 'network_error')


class InvalidVideoIdError(YouTubeAPIError):
    def __init__(self, message='Invalid video ID or URL.'):
        super().__init__(message, 'invalid_video_id')


class PrivateVideoError(YouTubeAPIError):
    def __init__(self, message='This video is private or unavailable.'):
        super().__init__(message, 'private_video')


class YouTubeService:
    VIDEO_ID_PATTERNS = [
        re.compile(r'(?:youtube\.com\/watch\?v=)([\w-]{11})'),
        re.compile(r'(?:youtu\.be\/)([\w-]{11})'),
        re.compile(r'(?:youtube\.com\/embed\/)([\w-]{11})'),
        re.compile(r'(?:youtube\.com\/v\/)([\w-]{11})'),
        re.compile(r'(?:youtube\.com\/shorts\/)([\w-]{11})'),
    ]

    @staticmethod
    def extract_video_id(url_or_id):
        url_or_id = url_or_id.strip()

        if re.match(r'^[\w-]{11}$', url_or_id):
            return url_or_id

        for pattern in YouTubeService.VIDEO_ID_PATTERNS:
            match = pattern.search(url_or_id)
            if match:
                return match.group(1)

        return None

    @staticmethod
    def _parse_youtube_datetime(dt_str):
        if not dt_str:
            return None
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt
        except (ValueError, TypeError):
            return None

    def fetch_video_info(self, video_id):
        api_key = current_app.config.get('YOUTUBE_API_KEY', '')
        if not api_key:
            raise YouTubeAPIError('YouTube API key not configured.', 'missing_api_key')

        try:
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError

            youtube = build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
            request = youtube.videos().list(part='snippet,statistics', id=video_id)
            response = request.execute()

            if not response.get('items'):
                raise VideoNotFoundError()

            item = response['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})

            return {
                'video_id': video_id,
                'title': snippet.get('title', 'Unknown Title'),
                'description': snippet.get('description', ''),
                'channel': snippet.get('channelTitle', 'Unknown Channel'),
                'published_at': self._parse_youtube_datetime(snippet.get('publishedAt')),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
            }
        except HttpError as e:
            status = e.resp.status if hasattr(e, 'resp') else 0
            if status == 403:
                body = str(e)
                if 'quota' in body.lower():
                    raise QuotaExceededError()
                raise YouTubeAPIError('YouTube API access denied. Check your API key.', 'access_denied')
            elif status == 404:
                raise VideoNotFoundError()
            else:
                raise YouTubeAPIError(f'YouTube API error (HTTP {status}).', 'api_error')
        except YouTubeAPIError:
            raise
        except Exception as e:
            current_app.logger.error(f"YouTube API error: {traceback.format_exc()}")
            if 'timeout' in str(e).lower() or 'connection' in str(e).lower():
                raise NetworkError()
            raise YouTubeAPIError('An unexpected error occurred with the YouTube API.', 'api_error')

    def fetch_comments(self, video_id, max_results=100):
        api_key = current_app.config.get('YOUTUBE_API_KEY', '')
        if not api_key:
            raise YouTubeAPIError('YouTube API key not configured.', 'missing_api_key')

        try:
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError

            youtube = build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
            comments = []
            next_page_token = None
            page_count = 0
            max_pages = 10

            while len(comments) < max_results and page_count < max_pages:
                remaining = max_results - len(comments)
                request = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, remaining),
                    pageToken=next_page_token
                )
                response = request.execute()

                items = response.get('items', [])
                if not items:
                    break

                for item in items:
                    snippet = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'text': snippet.get('textDisplay', ''),
                        'author': snippet.get('authorDisplayName', 'Unknown'),
                        'published_at': self._parse_youtube_datetime(snippet.get('publishedAt')),
                    })

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

                page_count += 1

            return comments

        except HttpError as e:
            status = e.resp.status if hasattr(e, 'resp') else 0
            error_body = str(e)

            if status == 403:
                if 'quota' in error_body.lower():
                    raise QuotaExceededError()
                if 'commentsDisabled' in error_body or 'disabled' in error_body.lower():
                    raise CommentsDisabledError()
                raise YouTubeAPIError('YouTube API access denied.', 'access_denied')
            elif status == 404:
                raise VideoNotFoundError()
            else:
                raise YouTubeAPIError(f'YouTube API error (HTTP {status}).', 'api_error')
        except YouTubeAPIError:
            raise
        except Exception as e:
            current_app.logger.error(f"YouTube API error: {traceback.format_exc()}")
            if 'timeout' in str(e).lower() or 'connection' in str(e).lower():
                raise NetworkError()
            raise YouTubeAPIError('An unexpected error occurred fetching comments.', 'api_error')
