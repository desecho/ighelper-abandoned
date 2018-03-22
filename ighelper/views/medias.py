import json

from babel.dates import format_date

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
        media['content'] = m.content
        media['id'] = m.id
        media['likes'] = m.likes_count
        media['views'] = m.views_count
        media['caption'] = m.caption_formatted
        media['location'] = m.location_formatted
        media['date'] = format_date(m.date, locale=user.language)
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
                video=m['video'],
                views_count=m['views_count'])

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
