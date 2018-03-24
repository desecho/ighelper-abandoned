import json

from babel.dates import format_date

from ighelper.models import InstagramUser, Like, Media

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
        if not m.location_name:
            media['noLocation'] = True
        media.update({
            'image': m.image,
            'imageSmall': m.image_small,
            'content': m.content,
            'id': m.id,
            'likes': m.likes_count,
            'views': m.views_count,
            'caption': m.caption_formatted,
            'location': m.location_formatted,
            'date': format_date(m.date, locale=user.language),
        })
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
            Media.objects.create(user=self.user, **m)

        return self.success(medias=get_medias(self.user))


class UpdateMediasView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        instagram_medias = self.instagram.get_medias()
        instagram_medias = {m['instagram_id']: m for m in instagram_medias}
        medias = self.user.medias.all()
        medias_instagram_ids = medias.values_list('instagram_id', flat=True)
        for media_instagram_id in medias_instagram_ids:
            medias_found = medias.filter(instagram_id=media_instagram_id)
            if medias_found.exists():
                medias_found.update(**instagram_medias[media_instagram_id])
            else:
                medias_found.delete()
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
        media.location_name = instagram_media['location_name']
        media.city = instagram_media['city']
        media.views_count = instagram_media['views_count']
        media.image = instagram_media['image']
        media.save()
        return self.success(media=get_medias(self.user, media_id)[0])

    def delete(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.success()


class CaptionUpdateView(InstagramAjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        try:
            caption = self.request.PUT['caption']
        except KeyError:
            return self.render_bad_request_response()

        self.get_data()
        media_id = kwargs['id']
        media = self.user.medias.get(pk=media_id)
        success = self.instagram.update_media_caption(media.instagram_id, caption)
        if success:
            media.caption = caption
            media.save()
            return self.success()

        media.delete()
        return self.fail()


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
        return self.success(medias=get_medias(self.user))


class LoadViewsView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        videos = self.user.videos.all()
        for video in videos:
            instagram_media = self.instagram.get_media(video.instagram_id)
            if instagram_media is None:
                media.delete()
                return self.fail()
            video.views_count = instagram_media['views_count']
            video.save()

        return self.success(medias=get_medias(self.user))
