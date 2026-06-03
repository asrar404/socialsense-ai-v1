import re
import traceback
from flask import current_app


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

    def fetch_video_info(self, video_id):
        api_key = current_app.config.get('YOUTUBE_API_KEY', '')
        if not api_key:
            return None

        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=api_key)
            request = youtube.videos().list(part='snippet,statistics', id=video_id)
            response = request.execute()

            if not response.get('items'):
                return None

            item = response['items'][0]
            snippet = item['snippet']
            statistics = item.get('statistics', {})

            return {
                'video_id': video_id,
                'title': snippet.get('title', 'Unknown Title'),
                'channel': snippet.get('channelTitle', 'Unknown Channel'),
                'comment_count': int(statistics.get('commentCount', 0)),
            }
        except Exception:
            current_app.logger.error(f"YouTube API error: {traceback.format_exc()}")
            return None

    def fetch_comments(self, video_id, max_results=50):
        api_key = current_app.config.get('YOUTUBE_API_KEY', '')
        if not api_key:
            return None

        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=api_key)
            comments = []
            next_page_token = None

            while len(comments) < max_results:
                request = youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=next_page_token
                )
                response = request.execute()

                for item in response.get('items', []):
                    snippet = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'text': snippet.get('textDisplay', ''),
                        'author': snippet.get('authorDisplayName', 'Unknown'),
                    })

                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break

            return comments
        except Exception:
            current_app.logger.error(f"YouTube API error: {traceback.format_exc()}")
            return None
