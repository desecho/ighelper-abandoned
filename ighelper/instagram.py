import time
from datetime import datetime

from django.conf import settings
from InstagramAPI import InstagramAPI

from ighelper.models import Media


class Instagram:
    def __init__(self, username, password, instagram_id):
        self.api = InstagramAPI(username, password)
        self.api.login()
        self.id = instagram_id

    def get_followers(self):
        self.api.getUserFollowers(self.id)
        followers = self.api.LastJson['users']
        return [{
            'id': x['pk'],
            'username': x['username'],
            'name': x['full_name'],
            'avatar': x['profile_pic_url']
        } for x in followers]

    def get_medias(self):
        def get_video(media):
            if media['media_type'] == Media.MEDIA_TYPE_VIDEO:
                return media['video_versions'][0]['url']
            return None

        def get_location(media):
            if 'location' in media:
                return media['location']['name']
            return ''

        def get_text(media):
            if 'caption' in media and media['caption']:
                return media['caption']['text']
            return ''

        self.api.getUsernameInfo(self.id)
        media_number = self.api.LastJson['user']['media_count']

        medias = []
        max_id = ''
        pages = media_number // 18
        for i in range(pages + 1):
            self.api.getUserFeed(usernameId=self.id, maxid=max_id)
            medias += self.api.LastJson['items']
            if not self.api.LastJson['more_available']:
                break
            max_id = self.api.LastJson['next_max_id']
            page = i + 1
            print(f'Loaded {page} / {pages}')
            time.sleep(settings.MEDIA_SLEEP)

        medias_output = []
        for m in medias:
            media = {
                'id': m['id'],
                'media_type': m['media_type'],
                'date': datetime.fromtimestamp(m['taken_at']),
                'text': get_text(m),
                'location': get_location(m),
                'image': m['image_versions2']['candidates'][0]['url'],
                'video': get_video(m)
            }
            medias_output.append(media)

        return medias_output

    def get_likes(self, medias):
        i = 0
        total_medias = len(medias)
        likes = []
        for media in medias:
            i += 1
            self.api.getMediaLikers(media.instagram_id)
            users = self.api.LastJson['users']
            for user in users:
                like = {
                    'media': media,
                    'user_instagram_id': user['pk'],
                }
                likes.append(like)
            print(f'Loaded {i} / {total_medias}')
        return likes
