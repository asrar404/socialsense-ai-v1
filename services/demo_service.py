import random


class DemoService:
    DEMO_VIDEOS = [
        {
            'video_id': 'dQw4w9WgXcQ',
            'title': 'Demo Video - Product Review',
            'channel': 'Demo Channel',
            'comment_count': 25,
        },
        {
            'video_id': 'jNQXAC9IVRw',
            'title': 'Demo Video - Tech Tutorial',
            'channel': 'Demo Tech',
            'comment_count': 25,
        },
    ]

    DEMO_COMMENTS = [
        {"text": "Great video! Very informative and well presented.", "author": "User123"},
        {"text": "First comment! Love this content.", "author": "FastViewer99"},
        {"text": "Check out my channel for similar content! link in bio", "author": "PromoQueen"},
        {"text": "This is terrible. Worst video I've ever seen. You should delete this.", "author": "Hater2000"},
        {"text": "Nice video. Thanks for sharing.", "author": "CasualViewer"},
        {"text": "BUY NOW!!! Limited offer!!! Click the link!!!", "author": "SpamBot_X"},
        {"text": "I completely agree with your points. Well said.", "author": "ThoughtfulMike"},
        {"text": "Meh, it was okay I guess.", "author": "NeutralNancy"},
        {"text": "This changed my life. Thank you so much for making this.", "author": "GratefulFan"},
        {"text": "I have analyzed the market trends and this aligns with Q4 projections. The strategic implementation shows clear ROI potential.", "author": "BizAnalystPro"},
        {"text": "Nice try, but this misses the mark completely.", "author": "Critic101"},
        {"text": "subscribe to my channel please please please please please", "author": "DesperateGamer"},
        {"text": "Wow just wow amazing content keep it up!", "author": "Enthusiast22"},
        {"text": "This is so boring I fell asleep watching zzzzz", "author": "SleepyViewer"},
        {"text": "Great video! Very informative and well presented.", "author": "CloneUser1"},
        {"text": "Great video! Very informative!", "author": "CloneUser2"},
        {"text": "I think you should consider the alternative perspective on this topic.", "author": "DebateBro"},
        {"text": "Click here to win a free iPhone!!! http://spam-link.com", "author": "ScamAlert"},
        {"text": "I love your channel. Been watching for years. This is definitely one of your best.", "author": "LoyalSub"},
        {"text": "The production quality is outstanding. The editing and pacing are perfect. The content is well-researched. The presentation is clear. The examples are relevant. The conclusion is compelling.", "author": "OverlyStructured"},
        {"text": "lol", "author": "LaughingGuy"},
        {"text": "I disagree with your analysis of the situation.", "author": "DisagreeDan"},
        {"text": "spam spam spam spam spam spam spam spam spam spam", "author": "SpamBot_Y"},
        {"text": "Perfect timing! I was just looking for this information.", "author": "LuckyViewer"},
        {"text": "Not bad, could be better though.", "author": "MehSayer"},
    ]

    def get_video_info(self):
        video = random.choice(self.DEMO_VIDEOS)
        return {
            'video_id': video['video_id'],
            'title': video['title'],
            'channel': video['channel'],
            'comment_count': len(self.DEMO_COMMENTS),
            'is_demo': True,
        }

    def get_video_info_by_id(self, video_id):
        return {
            'video_id': video_id,
            'title': f'Demo Video ({video_id})',
            'channel': 'Demo Channel',
            'comment_count': len(self.DEMO_COMMENTS),
            'is_demo': True,
        }

    def get_comments(self):
        return self.DEMO_COMMENTS
