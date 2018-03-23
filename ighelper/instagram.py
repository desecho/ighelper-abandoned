import json
from datetime import datetime

from django.conf import settings
from InstagramAPI import InstagramAPI

from ighelper.exceptions import InstagramException
from ighelper.helpers import get_name
from ighelper.models import Media


class Instagram:
    _MESSAGE_MEDIA_NOT_FOUND = 'Media not found or unavailable'
    _MESSAGE_MEDIA_NOT_FOUND2 = 'You cannot edit this media'
    _MESSAGE_MEDIA_NOT_FOUND3 = 'Sorry, this photo has been deleted.'

    def __init__(self, username, password):
        self._api = InstagramAPI(username, password)
        self._api.login()

    def get_followers(self):
        self._api.getSelfUserFollowers()
        followers = self._api.LastJson['users']
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
                return media['location']['name'], media['location']['city']
            return ''

        def get_caption(media):
            if 'caption' in media and media['caption']:
                return media['caption']['text']
            return ''

        def get_views_count(media):
            if 'view_count' in media:
                return media['view_count']
            return None

        location_name, city = get_location(m)
        return {
            'instagram_id': m['id'],
            'media_type': m['media_type'],
            'date': datetime.fromtimestamp(m['taken_at']),
            'caption': get_caption(m),
            'location_name': location_name,
            'city': city,
            'image': m['image_versions2']['candidates'][0]['url'],
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
        media_number = self._api.LastJson['user']['media_count']

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

    def get_likes_and_deleted_medias(self, medias):
        """
        Return a tuple - (likes, deleted_medias) - (list of dicts, 'deleted_medias': list).
        """
        i = 0
        total_medias = len(medias)
        likes = []
        medias_deleted = []
        for media in medias:
            i += 1
            success = self._api.getMediaLikers(media.instagram_id)
            result = self._api.LastJson
            if success:
                users = result['users']
                for user in users:
                    like = {
                        'media': media,
                        'user_instagram_id': user['pk'],
                    }
                    likes.append(like)
            else:
                if 'message' in result and result['message'] == self._MESSAGE_MEDIA_NOT_FOUND3:
                    medias_deleted.append(media.id)
                else:
                    api_response = json.dumps(result)
                    raise InstagramException(f'Error getting media likes. API response - {api_response}')
            print(f'Loaded {i} / {total_medias}')

        return likes, medias_deleted

    def get_users_i_am_following(self):
        self._api.getSelfUsersFollowing()
        users = self._api.LastJson['users']
        return [{'id': user['pk'], 'name': get_name(user['full_name'], user['username'])} for user in users]

    def update_media_caption(self, media_id, caption):
        """
        Return True on success and False on failure.
        """
        success = self._api.editMedia(media_id, caption)
        if success:
            return True
        result = self._api.LastJson
        if result['message'] == self._MESSAGE_MEDIA_NOT_FOUND2:
            return False

    def follow(self, user_id):
        return self._api.follow(user_id)

    def unfollow(self, user_id):
        return self._api.unfollow(user_id)

    def block(self, user_id):
        return self._api.block(user_id)
