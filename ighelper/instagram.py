import time
from datetime import datetime

from django.conf import settings
from InstagramAPI import InstagramAPI

from ighelper.helpers import get_name
from ighelper.models import Media


class Instagram:
    def __init__(self, username, password):
        self.api = InstagramAPI(username, password)
        self.api.login()

    def get_followers(self):
        self.api.getSelfUserFollowers()
        followers = self.api.LastJson['users']
        return [{
            'id': str(x['pk']),
            'username': x['username'],
            'name': x['full_name'],
            'avatar': x['profile_pic_url']
        } for x in followers]

    @staticmethod
    def _get_media_data(m):
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

        return {
            'id': m['id'],
            'media_type': m['media_type'],
            'date': datetime.fromtimestamp(m['taken_at']),
            'text': get_text(m),
            'location': get_location(m),
            'image': m['image_versions2']['candidates'][0]['url'],
            'video': get_video(m)
        }

    def get_media(self, media_id):
        self.api.mediaInfo(media_id)
        return self._get_media_data(self.api.LastJson['items'][0])

    def get_medias(self, media_ids):
        self.api.getSelfUsernameInfo()
        media_number = self.api.LastJson['user']['media_count']

        medias = []
        max_id = ''
        pages = media_number // settings.MEDIAS_PER_PAGE
        stop_loading = False
        for i in range(pages + 1):
            self.api.getSelfUserFeed(maxid=max_id)
            medias_on_page = self.api.LastJson['items']
            for media in medias_on_page:
                media_id = media['id']
                if media_id in media_ids:
                    stop_loading = True
                    break
                medias.append(media)
            if not self.api.LastJson['more_available']:
                stop_loading = True
            if stop_loading:
                break
            max_id = self.api.LastJson['next_max_id']
            page = i + 1
            print(f'Loaded {page} / {pages}')

        medias_output = []
        for m in medias:
            media = self._get_media_data(m)
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
                    'user_instagram_id': str(user['pk']),
                }
                likes.append(like)
            print(f'Loaded {i} / {total_medias}')
        return likes

    def get_users_i_am_following(self):
        self.api.getSelfUsersFollowing()
        users = self.api.LastJson['users']
        return [{'id': str(user['pk']), 'name': get_name(user['full_name'], user['username'])} for user in users]
