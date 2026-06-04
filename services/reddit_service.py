import re
import traceback
from datetime import datetime, timezone
from flask import current_app


class RedditAPIError(Exception):
    def __init__(self, message, error_type='reddit_api_error'):
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


class InvalidSubredditError(RedditAPIError):
    def __init__(self, message='Subreddit not found or does not exist.'):
        super().__init__(message, 'invalid_subreddit')


class PrivateSubredditError(RedditAPIError):
    def __init__(self, message='This subreddit is private and cannot be accessed.'):
        super().__init__(message, 'private_subreddit')


class RestrictedSubredditError(RedditAPIError):
    def __init__(self, message='This subreddit is restricted.'):
        super().__init__(message, 'restricted_subreddit')


class PostNotFoundError(RedditAPIError):
    def __init__(self, message='Reddit post not found.'):
        super().__init__(message, 'post_not_found')


class DeletedPostError(RedditAPIError):
    def __init__(self, message='This post has been deleted.'):
        super().__init__(message, 'deleted_post')


class LockedCommentsError(RedditAPIError):
    def __init__(self, message='Comments are locked on this post.'):
        super().__init__(message, 'locked_comments')


class RedditRateLimitError(RedditAPIError):
    def __init__(self, message='Reddit API rate limit exceeded. Try again later.'):
        super().__init__(message, 'rate_limit')


class MissingCredentialsError(RedditAPIError):
    def __init__(self, message='Reddit API credentials not configured.'):
        super().__init__(message, 'missing_credentials')


class NetworkError(RedditAPIError):
    def __init__(self, message='Network error contacting Reddit API.'):
        super().__init__(message, 'network_error')


class RedditService:
    POST_URL_PATTERNS = [
        re.compile(r'(?:www\.|old\.|new\.)?reddit\.com/r/(\w+)/comments/(\w+)'),
        re.compile(r'redd\.it/(\w+)'),
    ]

    SUBREDDIT_PATTERNS = [
        re.compile(r'(?:www\.|old\.|new\.)?reddit\.com/r/(\w+)'),
    ]

    @staticmethod
    def extract_post_id(url_or_id):
        url_or_id = url_or_id.strip()
        if re.match(r'^[\w]+$', url_or_id) and len(url_or_id) >= 4:
            return url_or_id
        for pattern in RedditService.POST_URL_PATTERNS:
            match = pattern.search(url_or_id)
            if match:
                if len(match.groups()) >= 2:
                    return match.group(2)
                return match.group(1)
        return None

    @staticmethod
    def extract_subreddit_name(url_or_name):
        url_or_name = url_or_name.strip()
        if re.match(r'^[\w]+$', url_or_name) and len(url_or_name) >= 2:
            return url_or_name.lower()
        for pattern in RedditService.SUBREDDIT_PATTERNS:
            match = pattern.search(url_or_name)
            if match:
                return match.group(1).lower()
        return None

    @staticmethod
    def extract_post_info(url_or_id):
        url_or_id = url_or_id.strip()
        post_id = RedditService.extract_post_id(url_or_id)
        subreddit = None
        if not post_id:
            return None
        for pattern in RedditService.POST_URL_PATTERNS:
            match = pattern.search(url_or_id)
            if match and len(match.groups()) >= 2:
                subreddit = match.group(1).lower()
                break
        return {
            'post_id': post_id,
            'subreddit': subreddit,
        }

    def _has_credentials(self):
        cid = current_app.config.get('REDDIT_CLIENT_ID', '')
        secret = current_app.config.get('REDDIT_CLIENT_SECRET', '')
        return bool(cid) and bool(secret)

    def fetch_subreddit_info(self, subreddit_name):
        if not self._has_credentials():
            raise MissingCredentialsError()
        try:
            import requests
            cid = current_app.config['REDDIT_CLIENT_ID']
            secret = current_app.config['REDDIT_CLIENT_SECRET']
            ua = current_app.config.get('REDDIT_USER_AGENT', 'SocialSenseAI/1.0')

            auth = requests.auth.HTTPBasicAuth(cid, secret)
            data = {'grant_type': 'client_credentials'}
            headers = {'User-Agent': ua}

            token_resp = requests.post('https://www.reddit.com/api/v1/access_token',
                                       auth=auth, data=data, headers=headers, timeout=10)
            if token_resp.status_code != 200:
                raise RedditAPIError('Failed to authenticate with Reddit API.', 'auth_error')

            token = token_resp.json().get('access_token')
            headers['Authorization'] = f'bearer {token}'

            about_resp = requests.get(f'https://oauth.reddit.com/r/{subreddit_name}/about',
                                      headers=headers, timeout=10)
            if about_resp.status_code == 404:
                raise InvalidSubredditError()
            if about_resp.status_code == 403:
                raise PrivateSubredditError()
            if about_resp.status_code != 200:
                raise RedditAPIError(f'Reddit API returned status {about_resp.status_code}.')

            data = about_resp.json().get('data', {})
            return {
                'subreddit': subreddit_name,
                'title': data.get('title', subreddit_name),
                'subscribers': data.get('subscribers', 0),
                'active_users': data.get('accounts_active', 0) or data.get('active_user_count', 0),
                'description': data.get('public_description', ''),
                'created_utc': datetime.fromtimestamp(data.get('created_utc', 0), tz=timezone.utc) if data.get('created_utc') else None,
            }
        except requests.exceptions.Timeout:
            raise NetworkError('Request to Reddit API timed out.')
        except requests.exceptions.ConnectionError:
            raise NetworkError('Could not connect to Reddit API.')
        except RedditAPIError:
            raise
        except Exception as e:
            current_app.logger.error(f"Reddit API error: {traceback.format_exc()}")
            raise RedditAPIError('An unexpected error occurred with the Reddit API.')

    def fetch_post_info(self, post_id):
        if not self._has_credentials():
            raise MissingCredentialsError()
        try:
            import requests
            cid = current_app.config['REDDIT_CLIENT_ID']
            secret = current_app.config['REDDIT_CLIENT_SECRET']
            ua = current_app.config.get('REDDIT_USER_AGENT', 'SocialSenseAI/1.0')

            auth = requests.auth.HTTPBasicAuth(cid, secret)
            data = {'grant_type': 'client_credentials'}
            headers = {'User-Agent': ua}

            token_resp = requests.post('https://www.reddit.com/api/v1/access_token',
                                       auth=auth, data=data, headers=headers, timeout=10)
            if token_resp.status_code != 200:
                raise RedditAPIError('Failed to authenticate with Reddit API.')

            token = token_resp.json().get('access_token')
            headers['Authorization'] = f'bearer {token}'

            info_resp = requests.get(f'https://oauth.reddit.com/api/info?id=t3_{post_id}',
                                     headers=headers, timeout=10)
            if info_resp.status_code != 200:
                raise PostNotFoundError()

            listings = info_resp.json()
            if not listings or not listings.get('data') or not listings['data'].get('children'):
                raise PostNotFoundError()

            post_data = listings['data']['children'][0]['data']

            if post_data.get('removed_by_category') or post_data.get('removed'):
                raise DeletedPostError()

            created = datetime.fromtimestamp(post_data.get('created_utc', 0), tz=timezone.utc) if post_data.get('created_utc') else None

            return {
                'post_id': post_id,
                'subreddit': post_data.get('subreddit', ''),
                'title': post_data.get('title', ''),
                'body': post_data.get('selftext', ''),
                'author': post_data.get('author', '[deleted]'),
                'score': post_data.get('score', 0),
                'upvote_ratio': post_data.get('upvote_ratio', 0.0),
                'comment_count': post_data.get('num_comments', 0),
                'created_utc': created,
                'permalink': post_data.get('permalink', ''),
                'is_locked': post_data.get('locked', False),
                'is_archived': post_data.get('archived', False),
            }
        except requests.exceptions.Timeout:
            raise NetworkError('Request to Reddit API timed out.')
        except requests.exceptions.ConnectionError:
            raise NetworkError('Could not connect to Reddit API.')
        except RedditAPIError:
            raise
        except Exception as e:
            current_app.logger.error(f"Reddit API error: {traceback.format_exc()}")
            raise RedditAPIError('An unexpected error occurred with the Reddit API.')

    def fetch_comments(self, post_id, max_results=100):
        if not self._has_credentials():
            raise MissingCredentialsError()
        try:
            import requests
            cid = current_app.config['REDDIT_CLIENT_ID']
            secret = current_app.config['REDDIT_CLIENT_SECRET']
            ua = current_app.config.get('REDDIT_USER_AGENT', 'SocialSenseAI/1.0')

            auth = requests.auth.HTTPBasicAuth(cid, secret)
            data = {'grant_type': 'client_credentials'}
            headers = {'User-Agent': ua}

            token_resp = requests.post('https://www.reddit.com/api/v1/access_token',
                                       auth=auth, data=data, headers=headers, timeout=10)
            if token_resp.status_code != 200:
                raise RedditAPIError('Failed to authenticate with Reddit API.')

            token = token_resp.json().get('access_token')
            headers['Authorization'] = f'bearer {token}'

            limit = min(max_results, 100)
            comments_resp = requests.get(
                f'https://oauth.reddit.com/r/all/comments/{post_id}',
                headers=headers,
                params={'limit': limit, 'sort': 'top', 'depth': 1},
                timeout=10
            )
            if comments_resp.status_code != 200:
                raise PostNotFoundError()

            data = comments_resp.json()
            if not data or len(data) < 2:
                return []

            comments_data = data[1] if len(data) > 1 else data[0]
            if not comments_data or not comments_data.get('data') or not comments_data['data'].get('children'):
                return []

            comments = []
            self._flatten_comments(comments_data['data']['children'], comments, max_results)

            return comments
        except requests.exceptions.Timeout:
            raise NetworkError('Request to Reddit API timed out.')
        except requests.exceptions.ConnectionError:
            raise NetworkError('Could not connect to Reddit API.')
        except RedditAPIError:
            raise
        except Exception as e:
            current_app.logger.error(f"Reddit API error: {traceback.format_exc()}")
            raise RedditAPIError('An unexpected error occurred fetching Reddit comments.')

    def _flatten_comments(self, children, comments, max_results, depth=0):
        if depth > 5:
            return
        for child in children:
            if len(comments) >= max_results:
                return
            kind = child.get('kind', '')
            data = child.get('data', {})
            if kind == 't1' and data:
                body = data.get('body', '')
                if body and body not in ('[deleted]', '[removed]'):
                    created = datetime.fromtimestamp(data.get('created_utc', 0), tz=timezone.utc) if data.get('created_utc') else None
                    comments.append({
                        'text': body,
                        'author': data.get('author', '[deleted]'),
                        'score': data.get('score', 0),
                        'published_at': created,
                    })
            replies = data.get('replies')
            if replies and isinstance(replies, dict):
                reply_children = replies.get('data', {}).get('children', [])
                self._flatten_comments(reply_children, comments, max_results, depth + 1)


class RedditDemoService:
    DEMO_SUBREDDITS = [
        {'name': 'technology', 'title': 'Technology', 'subscribers': 15000000, 'active_users': 45000},
        {'name': 'AskReddit', 'title': 'AskReddit', 'subscribers': 42000000, 'active_users': 120000},
    ]

    DEMO_POSTS = [
        {
            'post_id': 'abc123',
            'subreddit': 'technology',
            'title': 'Demo Post - New AI Breakthrough Announced',
            'body': 'A major breakthrough in artificial intelligence has been announced today. Researchers have developed a new model that demonstrates significant improvements in natural language understanding.',
            'author': 'TechNewsBot',
            'score': 15420,
            'upvote_ratio': 0.89,
            'comment_count': 25,
            'permalink': '/r/technology/comments/abc123/',
            'created_utc': datetime(2024, 6, 15, tzinfo=timezone.utc),
        },
        {
            'post_id': 'def456',
            'subreddit': 'AskReddit',
            'title': 'Demo Post - What is your opinion on AI?',
            'body': '',
            'author': 'CuriousUser',
            'score': 8900,
            'upvote_ratio': 0.92,
            'comment_count': 25,
            'permalink': '/r/AskReddit/comments/def456/',
            'created_utc': datetime(2024, 7, 1, tzinfo=timezone.utc),
        },
    ]

    DEMO_COMMENTS = [
        {"text": "This is really interesting! I've been following this technology for years.", "author": "TechFan42", "score": 450, "published_at": datetime(2024, 6, 15, 10, 30, tzinfo=timezone.utc)},
        {"text": "Great post! Thanks for sharing this information.", "author": "HappyReader", "score": 230, "published_at": datetime(2024, 6, 15, 11, 0, tzinfo=timezone.utc)},
        {"text": "Check out my subreddit for more content like this! /r/mycontent", "author": "PromoKing", "score": -5, "published_at": datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)},
        {"text": "This is completely wrong. You clearly don't understand the subject.", "author": "AngryCritic", "score": -120, "published_at": datetime(2024, 6, 15, 13, 0, tzinfo=timezone.utc)},
        {"text": "I disagree with your analysis of the situation. There are several factors being overlooked here.", "author": "DebateLord", "score": 89, "published_at": datetime(2024, 6, 15, 14, 0, tzinfo=timezone.utc)},
        {"text": "Nice try, but this misses the mark completely. Do better next time.", "author": "HarshCritic", "score": -30, "published_at": datetime(2024, 6, 15, 15, 0, tzinfo=timezone.utc)},
        {"text": "I have analyzed the market trends and this aligns with Q4 projections. The strategic implementation shows clear ROI potential. First of all, we need to consider the broader implications. Furthermore, the data suggests a positive trend. In conclusion, this is a significant development.", "author": "BizAnalystPro", "score": 312, "published_at": datetime(2024, 6, 15, 16, 0, tzinfo=timezone.utc)},
        {"text": "lol", "author": "LaughMaster", "score": 200, "published_at": datetime(2024, 6, 15, 17, 0, tzinfo=timezone.utc)},
        {"text": "This is the worst take I've ever seen. You should delete this post.", "author": "ToxicUser", "score": -200, "published_at": datetime(2024, 6, 15, 18, 0, tzinfo=timezone.utc)},
        {"text": "BUY NOW!!! Limited offer!!! Click the link in my profile!!!", "author": "SpamBot999", "score": -50, "published_at": datetime(2024, 6, 15, 19, 0, tzinfo=timezone.utc)},
        {"text": "Thank you for posting this. Very helpful and informative.", "author": "GratefulReader", "score": 150, "published_at": datetime(2024, 6, 16, 8, 0, tzinfo=timezone.utc)},
        {"text": "This changed my perspective on the whole issue. Well written!", "author": "MindChanged", "score": 500, "published_at": datetime(2024, 6, 16, 9, 0, tzinfo=timezone.utc)},
        {"text": "Can you provide sources for your claims?", "author": "SkepticalUser", "score": 75, "published_at": datetime(2024, 6, 16, 10, 0, tzinfo=timezone.utc)},
        {"text": "subscribe to my newsletter for daily updates please please please", "author": "SpammySpammer", "score": -10, "published_at": datetime(2024, 6, 16, 11, 0, tzinfo=timezone.utc)},
        {"text": "Meh, it's okay I guess. Not as good as the previous one.", "author": "NeutralNed", "score": 10, "published_at": datetime(2024, 6, 16, 12, 0, tzinfo=timezone.utc)},
        {"text": "Wow just wow! Amazing post! Keep up the great work!", "author": "Enthusiast99", "score": 180, "published_at": datetime(2024, 6, 16, 13, 0, tzinfo=timezone.utc)},
        {"text": "I think you should consider the alternative perspective on this topic before making such strong claims.", "author": "LevelHead", "score": 95, "published_at": datetime(2024, 6, 16, 14, 0, tzinfo=timezone.utc)},
        {"text": "spam spam spam spam spam spam spam spam spam spam spam spam", "author": "SpamBot_XYZ", "score": -100, "published_at": datetime(2024, 6, 16, 15, 0, tzinfo=timezone.utc)},
        {"text": "This is terrible. Absolutely the worst post on this subreddit.", "author": "HaterHater", "score": -80, "published_at": datetime(2024, 6, 16, 16, 0, tzinfo=timezone.utc)},
        {"text": "Great post! Very informative and well presented.", "author": "CloneUser1", "score": 80, "published_at": datetime(2024, 6, 17, 8, 0, tzinfo=timezone.utc)},
        {"text": "Great post! Very informative!", "author": "CloneUser2", "score": 60, "published_at": datetime(2024, 6, 17, 8, 5, tzinfo=timezone.utc)},
        {"text": "I completely agree with the OP. Well said.", "author": "AgreeableAndy", "score": 120, "published_at": datetime(2024, 6, 17, 9, 0, tzinfo=timezone.utc)},
        {"text": "The quality of this subreddit has really gone downhill.", "author": "OldTimer", "score": -45, "published_at": datetime(2024, 6, 17, 10, 0, tzinfo=timezone.utc)},
        {"text": "RemindMe! 2 days", "author": "RemindBot", "score": 300, "published_at": datetime(2024, 6, 17, 11, 0, tzinfo=timezone.utc)},
        {"text": "Not bad, could be better though. Needs more detail.", "author": "CritiqueQueen", "score": 15, "published_at": datetime(2024, 6, 17, 12, 0, tzinfo=timezone.utc)},
    ]

    def get_subreddit_info(self, subreddit_name):
        return {
            'subreddit': subreddit_name,
            'title': f'r/{subreddit_name}',
            'subscribers': 5000000,
            'active_users': 15000,
            'description': 'A demo subreddit for testing SocialSense AI features.',
            'created_utc': datetime(2020, 1, 1, tzinfo=timezone.utc),
            'is_demo': True,
        }

    def get_post_info(self, post_id, subreddit=None):
        return {
            'post_id': post_id,
            'subreddit': subreddit or 'technology',
            'title': f'Demo Reddit Post ({post_id})',
            'body': 'This is a demo Reddit post used for testing SocialSense AI features.',
            'author': 'DemoAuthor',
            'score': 10000,
            'upvote_ratio': 0.85,
            'comment_count': len(self.DEMO_COMMENTS),
            'created_utc': datetime(2024, 6, 15, tzinfo=timezone.utc),
            'permalink': f'/r/technology/comments/{post_id}/',
            'is_locked': False,
            'is_archived': False,
            'is_demo': True,
        }

    def get_comments(self):
        return self.DEMO_COMMENTS
