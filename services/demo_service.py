import random
from datetime import datetime, timezone


class DemoService:
    DEMO_VIDEOS = [
        {
            'video_id': 'dQw4w9WgXcQ',
            'title': 'Demo Video - Product Review',
            'description': 'A comprehensive review of the latest tech product. We test all features and give our honest opinion.',
            'channel': 'Demo Channel',
            'published_at': datetime(2024, 1, 15, tzinfo=timezone.utc),
            'view_count': 125000,
            'like_count': 8200,
            'comment_count': 25,
        },
        {
            'video_id': 'jNQXAC9IVRw',
            'title': 'Demo Video - Tech Tutorial',
            'description': 'Step by step tutorial showing you how to get started. Perfect for beginners.',
            'channel': 'Demo Tech',
            'published_at': datetime(2024, 3, 22, tzinfo=timezone.utc),
            'view_count': 89000,
            'like_count': 5400,
            'comment_count': 25,
        },
    ]

    DEMO_COMMENTS = [
        {"text": "Great video! Very informative and well presented.", "author": "User123", "published_at": datetime(2024, 1, 16, tzinfo=timezone.utc)},
        {"text": "First comment! Love this content.", "author": "FastViewer99", "published_at": datetime(2024, 1, 15, tzinfo=timezone.utc)},
        {"text": "Check out my channel for similar content! link in bio", "author": "PromoQueen", "published_at": datetime(2024, 1, 17, tzinfo=timezone.utc)},
        {"text": "This is terrible. Worst video I've ever seen. You should delete this.", "author": "Hater2000", "published_at": datetime(2024, 1, 18, tzinfo=timezone.utc)},
        {"text": "Nice video. Thanks for sharing.", "author": "CasualViewer", "published_at": datetime(2024, 1, 19, tzinfo=timezone.utc)},
        {"text": "BUY NOW!!! Limited offer!!! Click the link!!!", "author": "SpamBot_X", "published_at": datetime(2024, 1, 20, tzinfo=timezone.utc)},
        {"text": "I completely agree with your points. Well said.", "author": "ThoughtfulMike", "published_at": datetime(2024, 2, 1, tzinfo=timezone.utc)},
        {"text": "Meh, it was okay I guess.", "author": "NeutralNancy", "published_at": datetime(2024, 2, 3, tzinfo=timezone.utc)},
        {"text": "This changed my life. Thank you so much for making this.", "author": "GratefulFan", "published_at": datetime(2024, 2, 5, tzinfo=timezone.utc)},
        {"text": "I have analyzed the market trends and this aligns with Q4 projections. The strategic implementation shows clear ROI potential.", "author": "BizAnalystPro", "published_at": datetime(2024, 2, 10, tzinfo=timezone.utc)},
        {"text": "Nice try, but this misses the mark completely.", "author": "Critic101", "published_at": datetime(2024, 2, 12, tzinfo=timezone.utc)},
        {"text": "subscribe to my channel please please please please please", "author": "DesperateGamer", "published_at": datetime(2024, 2, 15, tzinfo=timezone.utc)},
        {"text": "Wow just wow amazing content keep it up!", "author": "Enthusiast22", "published_at": datetime(2024, 2, 18, tzinfo=timezone.utc)},
        {"text": "This is so boring I fell asleep watching zzzzz", "author": "SleepyViewer", "published_at": datetime(2024, 3, 1, tzinfo=timezone.utc)},
        {"text": "Great video! Very informative and well presented.", "author": "CloneUser1", "published_at": datetime(2024, 3, 5, tzinfo=timezone.utc)},
        {"text": "Great video! Very informative!", "author": "CloneUser2", "published_at": datetime(2024, 3, 5, tzinfo=timezone.utc)},
        {"text": "I think you should consider the alternative perspective on this topic.", "author": "DebateBro", "published_at": datetime(2024, 3, 8, tzinfo=timezone.utc)},
        {"text": "Click here to win a free iPhone!!! http://spam-link.com", "author": "ScamAlert", "published_at": datetime(2024, 3, 10, tzinfo=timezone.utc)},
        {"text": "I love your channel. Been watching for years. This is definitely one of your best.", "author": "LoyalSub", "published_at": datetime(2024, 3, 12, tzinfo=timezone.utc)},
        {"text": "The production quality is outstanding. The editing and pacing are perfect. The content is well-researched. The presentation is clear. The examples are relevant. The conclusion is compelling.", "author": "OverlyStructured", "published_at": datetime(2024, 3, 15, tzinfo=timezone.utc)},
        {"text": "lol", "author": "LaughingGuy", "published_at": datetime(2024, 3, 18, tzinfo=timezone.utc)},
        {"text": "I disagree with your analysis of the situation.", "author": "DisagreeDan", "published_at": datetime(2024, 3, 20, tzinfo=timezone.utc)},
        {"text": "spam spam spam spam spam spam spam spam spam spam", "author": "SpamBot_Y", "published_at": datetime(2024, 3, 22, tzinfo=timezone.utc)},
        {"text": "Perfect timing! I was just looking for this information.", "author": "LuckyViewer", "published_at": datetime(2024, 3, 25, tzinfo=timezone.utc)},
        {"text": "Not bad, could be better though.", "author": "MehSayer", "published_at": datetime(2024, 3, 28, tzinfo=timezone.utc)},
    ]

    def get_video_info(self):
        video = random.choice(self.DEMO_VIDEOS)
        return {
            'video_id': video['video_id'],
            'title': video['title'],
            'description': video['description'],
            'channel': video['channel'],
            'published_at': video['published_at'],
            'view_count': video['view_count'],
            'like_count': video['like_count'],
            'comment_count': len(self.DEMO_COMMENTS),
            'is_demo': True,
        }

    def get_video_info_by_id(self, video_id):
        return {
            'video_id': video_id,
            'title': f'Demo Video ({video_id})',
            'description': 'This is a demo video used for testing SocialSense AI features.',
            'channel': 'Demo Channel',
            'published_at': datetime(2024, 6, 1, tzinfo=timezone.utc),
            'view_count': 50000,
            'like_count': 3200,
            'comment_count': len(self.DEMO_COMMENTS),
            'is_demo': True,
        }

    def get_comments(self):
        return self.DEMO_COMMENTS
