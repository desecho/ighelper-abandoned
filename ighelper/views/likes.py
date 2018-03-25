import json

from ighelper.models import InstagramUser, InstagramUserCounter, Like

from .mixins import InstagramAjaxView, TemplateView


def get_users_who_liked_medias_excluding_followers(user):
    followers = user.followers.values_list('instagram_user__pk', flat=True).distinct()
    instagram_user_counters = user.instagram_user_counters.exclude(instagram_user__in=followers)
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
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        try:
            only_for_new_medias = json.loads(self.request.POST['onlyForNewMedias'])
        except KeyError:
            return self.render_bad_request_response()

        self.get_data()
        medias = self.user.medias.all()
        if only_for_new_medias:
            medias = medias.filter(likes_count=0)
        media_ids = medias.values_list('instagram_id', flat=True)
        instagram_id_medias = {media.instagram_id: media for media in medias}
        likes, medias_deleted = self.instagram.get_likes_and_deleted_medias(media_ids)
        Like.objects.filter(media__user=self.user).delete()
        medias.filter(instagram_id__in=medias_deleted).delete()
        instagram_users_ids_updated = []
        instagram_users = set()
        for like in likes:
            instagram_user = like['user']
            instagram_user_id = instagram_user['instagram_id']
            instagram_users_found = InstagramUser.objects.filter(instagram_id=instagram_user_id)
            if instagram_users_found.exists():
                if instagram_user_id not in instagram_users_ids_updated:
                    instagram_users_found.update(**instagram_user)
                    instagram_users_ids_updated.append(instagram_user_id)
                instagram_user = instagram_users_found[0]
            else:
                instagram_user = InstagramUser.objects.create(**instagram_user)

            media = instagram_id_medias[like['media_instagram_id']]
            Like.objects.create(media=media, instagram_user=instagram_user)
            instagram_users.add(instagram_user)

        # Update likes counters
        for media in medias:
            media.likes_count = media.likes.count()
            media.save()

        InstagramUserCounter.objects.filter(user=self.user).delete()
        for instagram_user in instagram_users:
            likes_count = instagram_user.likes.filter(media__user=self.user).count()
            InstagramUserCounter.objects.create(user=self.user, instagram_user=instagram_user, likes_count=likes_count)

        return self.success(users=get_users_who_liked_medias_excluding_followers(self.user))
