import json
from datetime import datetime

from django.conf import settings
from InstagramAPI import InstagramAPI

from ighelper.exceptions import InstagramException
from ighelper.helpers import get_name
from ighelper.models import Media


class Instagram:
    _MEDIA_NOT_FOUND_MESSAGE = 'Media not found or unavailable'

    def __init__(self, username, password):
        self.api = InstagramAPI(username, password)
        self.api.login()

    def get_followers(self):
        self.api.getSelfUserFollowers()
        followers = self.api.LastJson['users']
        return [{
            'id': x['pk'],
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

        def get_caption(media):
            if 'caption' in media and media['caption']:
                return media['caption']['text']
            return ''

        return {
            'id': m['id'],
            'media_type': m['media_type'],
            'date': datetime.fromtimestamp(m['taken_at']),
            'caption': get_caption(m),
            'location': get_location(m),
            'image': m['image_versions2']['candidates'][0]['url'],
            'video': get_video(m)
        }

    def get_media(self, media_id):
        success = self.api.mediaInfo(media_id)
        result = self.api.LastJson
        if success:
            return self._get_media_data(['items'][0])

        if 'message' in result and result['message'] == self._MEDIA_NOT_FOUND_MESSAGE:
            return None
        else:
            api_response = json.dumps(result)
            raise InstagramException(f'Error getting media. API response - {api_response}')

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

    def get_likes_and_deleted_medias(self, medias):
        """
        Return a tuple - (likes, deleted_medias) - (list of dicts, 'deleted_medias': list)
        """
        i = 0
        total_medias = len(medias)
        likes = []
        medias_deleted = []
        for media in medias:
            i += 1
            success = self.api.getMediaLikers(media.instagram_id)
            result = self.api.LastJson
            if success:
                users = result['users']
                for user in users:
                    like = {
                        'media': media,
                        'user_instagram_id': user['pk'],
                    }
                    likes.append(like)
            else:
                if 'message' in result and result['message'] == 'Sorry, this photo has been deleted.':
                    medias_deleted.append(media.id)
                else:
                    api_response = json.dumps(result)
                    raise InstagramException(f'Error getting media likes. API response - {api_response}')
            print(f'Loaded {i} / {total_medias}')

        return likes, medias_deleted

    def get_users_i_am_following(self):
        self.api.getSelfUsersFollowing()
        users = self.api.LastJson['users']
        return [{'id': user['pk'], 'name': get_name(user['full_name'], user['username'])} for user in users]
