import json

from ighelper.models import Media

from .mixins import InstagramAjaxView, TemplateView


def get_medias(user, media_id=None):
    medias = user.medias.all()
    if media_id is not None:
        medias = medias.filter(id=media_id)
    medias_output = []
    for m in medias:
        media = {
            'noText': False,
            'noTags': False,
            'noLocation': False,
        }
        media_issue = False
        if not m.text:
            media['noText'] = True
            media['noTags'] = True
            media_issue = True
        elif '#' not in m.text:
            media['noTags'] = True
            media_issue = True
        if not m.location:
            media['noLocation'] = True
            media_issue = True
        # We want to output the info if we request a particular media.
        if media_issue or media_id:
            media['image'] = m.image
            media['id'] = m.id
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
                text=m['text'],
                location=m['location'],
                image=m['image'],
                video=m['video'])

        return self.success(medias=get_medias(self.user))


class UpdateMediaView(InstagramAjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        media_id = kwargs['id']
        media = self.user.medias.get(pk=media_id)
        instagram_media = self.instagram.get_media(media.instagram_id)
        media.text = instagram_media['text']
        media.location = instagram_media['location']
        media.save()
        return self.success(media=get_medias(self.user, media_id)[0])
