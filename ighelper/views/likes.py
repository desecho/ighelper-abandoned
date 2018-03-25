import json

from ighelper.models import InstagramUser, Like

from .mixins import InstagramAjaxView, TemplateView


class LikesView(TemplateView):
    template_name = 'likes.html'

    def get_context_data(self):
        users = self.request.user.get_users_who_liked_medias_excluding_followers()
        return {'users': json.dumps(users)}


class LoadLikesView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        medias = self.user.medias.all()
        media_ids = medias.values_list('instagram_id', flat=True)
        instagram_id_medias = {media.instagram_id: media for media in medias}
        likes, medias_deleted = self.instagram.get_likes_and_deleted_medias(media_ids)
        Like.objects.filter(media__user=self.user).delete()
        medias.filter(instagram_id__in=medias_deleted).delete()
        for like in likes:
            instagram_user = like['user']
            instagram_users = InstagramUser.objects.filter(instagram_id=instagram_user['instagram_id'])
            if instagram_users.exists():
                instagram_users.update(**instagram_user)
                instagram_user = instagram_users[0]
            else:
                instagram_user = InstagramUser.objects.create(**instagram_user)

            media = instagram_id_medias[like['media_instagram_id']]
            Like.objects.create(media=media, instagram_user=instagram_user)

        # Update likes counter
        for media in medias:
            media.likes_count = media.likes.count()
            media.save()
        return self.success(medias=get_medias(self.user.get_users_who_liked_medias_excluding_followers()))
