import json
from datetime import datetime

from django.conf import settings
from InstagramAPI import InstagramAPI

from ighelper.exceptions import (
    InstagramException,
    InstagramMediaNotFoundException,
)
from ighelper.models import Media


class Instagram:
    _MESSAGE_MEDIA_NOT_FOUND = 'Media not found or unavailable'
    _MESSAGE_MEDIA_NOT_FOUND2 = 'You cannot edit this media'
    _MESSAGE_MEDIA_NOT_FOUND3 = 'Sorry, this photo has been deleted.'

    def __init__(self, username, password):
        self._api = InstagramAPI(username, password)
        self._api.login()

    @staticmethod
    def _get_user_data(user):
        return {
            'instagram_id': user['pk'],
            'username': user['username'],
            'name': user['full_name'],
            'avatar': user['profile_pic_url']
        }

    def get_followers(self):
        self._api.getSelfUserFollowers()
        response = self._api.LastJson
        if 'users' not in response:
            response = json.dumps(response)
            raise InstagramException(f'Incorrect response. API response - {response}')

        return [self._get_user_data(user) for user in response['users']]

    def get_likes_and_deleted_medias(self, medias_ids):
        """
        Return a tuple - (likes, deleted_medias) - (list of dicts, 'deleted_medias': list).
        """
        i = 0
        total_medias = len(medias_ids)
        likes = []
        medias_deleted = []
        for media_id in medias_ids:
            i += 1
            success = self._api.getMediaLikers(media_id)
            result = self._api.LastJson
            if success:
                users = result['users']
                for user in users:
                    like = {
                        'media_instagram_id': media_id,
                        'user': self._get_user_data(user),
                    }
                    likes.append(like)
            else:
                if 'message' in result and result['message'] == self._MESSAGE_MEDIA_NOT_FOUND3:
                    medias_deleted.append(media_id)
                else:
                    api_response = json.dumps(result)
                    raise InstagramException(f'Error getting media likes. API response - {api_response}')
            print(f'Loaded {i} / {total_medias}')

        return likes, medias_deleted

    @staticmethod
    def _get_media_data(m):
        def get_video(media):
            if media['media_type'] == Media.MEDIA_TYPE_VIDEO:
                return media['video_versions'][0]['url']
            return None

        def get_location(media):
            if 'location' in media:
                return media['location']['name'], media['location']['city']
            return '', ''

        def get_caption(media):
            if 'caption' in media and media['caption']:
                return media['caption']['text']
            return ''

        def get_views_count(media):
            if 'view_count' in media:
                return media['view_count']
            return None

        location_name, city = get_location(m)
        images = m['image_versions2']['candidates']
        return {
            'instagram_id': m['id'],
            'media_type': m['media_type'],
            'date': datetime.fromtimestamp(m['taken_at']),
            'caption': get_caption(m),
            'location_name': location_name,
            'city': city,
            'image': images[0]['url'],
            'image_small': images[1]['url'],
            'video': get_video(m),
            'views_count': get_views_count(m),
        }

    def get_media(self, media_id):
        success = self._api.mediaInfo(media_id)
        result = self._api.LastJson
        if success:
            return self._get_media_data(result['items'][0])

        if 'message' in result and result['message'] == self._MESSAGE_MEDIA_NOT_FOUND:
            return None
        else:
            api_response = json.dumps(result)
            raise InstagramException(f'Error getting media. API response - {api_response}')

    def get_medias(self, media_ids=None):
        if media_ids is None:
            media_ids = []
        self._api.getSelfUsernameInfo()
        response = self._api.LastJson
        if 'user' not in response:
            response = json.dumps(response)
            raise InstagramException(f'Incorrect response. API response - {response}')

        media_number = response['user']['media_count']

        medias = []
        max_id = ''
        pages = media_number // settings.MEDIAS_PER_PAGE
        stop_loading = False
        for i in range(pages + 1):
            self._api.getSelfUserFeed(maxid=max_id)
            medias_on_page = self._api.LastJson['items']
            for media in medias_on_page:
                media_id = media['id']
                if media_id in media_ids:
                    stop_loading = True
                    break
                medias.append(media)
            if not self._api.LastJson['more_available']:
                stop_loading = True
            if stop_loading:
                break
            max_id = self._api.LastJson['next_max_id']
            page = i + 1
            print(f'Loaded {page} / {pages}')

        medias_output = []
        for m in medias:
            media = self._get_media_data(m)
            medias_output.append(media)

        return medias_output

    def get_followed(self):
        self._api.getSelfUsersFollowing()
        response = self._api.LastJson
        if 'users' not in response:
            response = json.dumps(response)
            raise InstagramException(f'Incorrect response. API response - {response}')
        users = response['users']
        return [self._get_user_data(user) for user in users]

    def update_media_caption(self, media_id, caption):
        success = self._api.editMedia(media_id, caption)
        if not success:
            response = self._api.LastJson
            if 'message' in response and response['message'] == self._MESSAGE_MEDIA_NOT_FOUND2:
                raise InstagramMediaNotFoundException()
            response = json.dumps(response)
            raise InstagramException(f'Error updating media caption. API response - {response}')

    def follow(self, user_id):
        success = self._api.follow(user_id)
        if not success:
            response = json.dumps(self._api.LastJson)
            raise InstagramException(f'Error following a user. API response - {response}')

    def unfollow(self, user_id):
        success = self._api.unfollow(user_id)
        if not success:
            response = json.dumps(self._api.LastJson)
            raise InstagramException(f'Error unfollowing a user. API response - {response}')

    def block(self, user_id):
        success = self._api.block(user_id)
        if not success:
            response = json.dumps(self._api.LastJson)
            raise InstagramException(f'Error blocking a user. API response - {response}')

    def delete_media(self, media_id):
        success = self._api.deleteMedia(media_id)
        if not success:
            response = json.dumps(self._api.LastJson)
            raise InstagramException(f'Error deleting media caption. API response - {response}')
