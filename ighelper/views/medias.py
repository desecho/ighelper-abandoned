import json

from django.utils.translation import gettext_lazy as _

from ighelper.models import Like, Media

from .mixins import InstagramAjaxView, TemplateView


def get_medias(user, media_id=None):
    medias = user.medias.all()
    if media_id is not None:
        medias = medias.filter(id=media_id)
    medias_output = []
    for m in medias:
        media = {
            'noCaption': False,
            'noTags': False,
            'noLocation': False,
        }
        if not m.caption:
            media['noCaption'] = True
            media['noTags'] = True
        elif '#' not in m.caption:
            media['noTags'] = True
        if not m.location:
            media['noLocation'] = True
        media['image'] = m.image
        media['id'] = m.id
        media['likes'] = m.likes_count
        media['caption'] = m.caption
        medias_output.append(media)
    return medias_output


class MediasView(TemplateView):
    template_name = 'medias.html'

    def get_context_data(self):
        medias = get_medias(self.request.user)
        return {'medias': json.dumps(medias)}


class LoadMediasView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        media_ids = self.user.medias.values_list('instagram_id', flat=True)
        medias = self.instagram.get_medias(media_ids)
        for m in medias:
            Media.objects.create(
                user=self.user,
                instagram_id=m['id'],
                media_type=m['media_type'],
                date=m['date'],
                caption=m['caption'],
                location=m['location'],
                image=m['image'],
                video=m['video'])

        return self.success(medias=get_medias(self.user))


class MediaView(InstagramAjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        media_id = kwargs['id']
        media = self.user.medias.get(pk=media_id)
        instagram_media = self.instagram.get_media(media.instagram_id)
        if instagram_media is None:
            media.delete()
            return self.fail()
        media.caption = instagram_media['caption']
        media.location = instagram_media['location']
        media.save()
        return self.success(media=get_medias(self.user, media_id)[0])

    def delete(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.success()


class LoadLikesView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        medias = self.user.medias.all()
        likes, medias_deleted = self.instagram.get_likes_and_deleted_medias(medias)
        Like.objects.filter(media__user=self.user).delete()
        self.user.medias.filter(pk__in=medias_deleted).delete()
        for l in likes:
            users = self.user.followers.filter(instagram_id=l['user_instagram_id'])
            if users.exists():
                follower = users[0]
            else:
                follower = None
            Like.objects.create(media=l['media'], follower=follower)

        # Update likes counter
        for media in medias:
            media.likes_count = media.likes.count()
            media.save()
        return self.success(medias=get_medias(self.user))
