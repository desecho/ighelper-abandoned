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
        followers = api.LastJson['users']
        return [{
            'id': x['pk'],
            'username': x['username'],
            'name': x['full_name'],
            'avatar': x['profile_pic_url']
        } for x in followers]

    def get_medias(self):
        def get_video():
            if m['media_type'] == Media.MEDIA_TYPE_VIDEO:
                return m['video_versions'][0]['url']
            return None

        def get_location():
            if 'location' in m:
                return m['location']['name']
            return ''

        def get_text():
            if 'caption' in m and m['caption']:
                return m['caption']['text']
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
                'text': get_text(),
                'location': get_location(),
                'image': m['image_versions2']['candidates'][0]['url'],
                'video': get_video()
            }
            medias_output.append(media)

        return medias_output
