import json

from django.utils.translation import gettext_lazy as _

from ighelper.models import InstagramUser, InstagramUserCounter, Like

from .mixins import InstagramAjaxView, TemplateView


def get_users_who_liked_medias_excluding_followers(user):
    instagram_user_counters = user.get_instagram_user_counters_of_users_who_are_not_followers_but_liked_media()
    users = []
    for instagram_user_counter in instagram_user_counters:
        user = instagram_user_counter.instagram_user
        user = {
            'profile': user.profile,
            'avatar': user.avatar,
            'name': str(user),
            'likes_count': instagram_user_counter.likes_count,
        }
        users.append(user)
    return users


class LikesView(TemplateView):
    template_name = 'likes.html'

    def get_context_data(self):
        users = get_users_who_liked_medias_excluding_followers(self.request.user)
        return {'users': json.dumps(users)}


class LoadLikesView(InstagramAjaxView):
    def _update_likes_counters(self, medias, instagram_users):
        for media in medias:
            media.likes_count = media.likes.count()
            media.save()

        InstagramUserCounter.objects.filter(user=self.user).delete()
        for instagram_user in instagram_users:
            likes_count = instagram_user.likes.filter(media__user=self.user).count()
            InstagramUserCounter.objects.create(user=self.user, instagram_user=instagram_user, likes_count=likes_count)

    @staticmethod
    def _get_instagram_users(instagram_users_data):
        instagram_users = {}
        for instagram_user in instagram_users_data:
            instagram_user_id = instagram_user['instagram_id']
            instagram_users_found = InstagramUser.objects.filter(instagram_id=instagram_user_id)
            if instagram_users_found.exists():
                instagram_users_found.update(**instagram_user)
                instagram_user = instagram_users_found[0]
            else:
                instagram_user = InstagramUser.objects.create(**instagram_user)
            instagram_users[instagram_user_id] = instagram_user
        return instagram_users

    def post(self, *args, **kwargs):  # pylint: disable=unused-argument,too-many-locals
        try:
            only_for_new_medias = json.loads(self.request.POST['onlyForNewMedias'])
        except KeyError:
            return self.render_bad_request_response()

        self.get_data()
        medias = self.user.medias.all()
        if not medias.exists():
            return self.fail(_('You need to load medias first'), self.MESSAGE_WARNING)

        if only_for_new_medias:
            medias = medias.filter(likes_count=0)
            if not medias.exists():
                return self.fail(_('There are no new medias'), self.MESSAGE_INFO)

        media_instagram_ids = medias.values_list('instagram_id', flat=True)
        instagram_id_medias = {media.instagram_id: media for media in medias}
        likes, instagram_users_data, media_instagram_ids_deleted = (
            self.instagram.get_likes_instagram_users_data_and_deleted_medias(media_instagram_ids))
        self.update_cache()
        Like.objects.filter(media__instagram_id__in=media_instagram_ids).delete()
        medias.filter(instagram_id__in=media_instagram_ids_deleted).delete()
        instagram_users = self._get_instagram_users(instagram_users_data)
        for media_instagram_id, instagram_user_ids in likes.items():
            media = instagram_id_medias[media_instagram_id]
            for instagram_user_id in instagram_user_ids:
                Like.objects.create(media=media, instagram_user=instagram_users[instagram_user_id])

        self._update_likes_counters(medias, instagram_users.values())
        return self.success(users=get_users_who_liked_medias_excluding_followers(self.user))
