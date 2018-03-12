import json

import requests
from django.conf import settings

from ighelper.instagram import Instagram
from ighelper.models import Follower, Media

from .mixins import AjaxView, TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self):
        user = self.request.user
        followers_number = user.followers.count()
        images_number = Media.images.filter(user=user).count()
        videos_number = Media.videos.filter(user=user).count()
        return {'followers_number': followers_number, 'images_number': images_number, 'videos_number': videos_number}


class FollowersView(TemplateView):
    template_name = 'followers.html'

    def get_context_data(self):
        def get_instagram_id():
            r = requests.get(f'{settings.INSTAGRAM_BASE_URL}/{user.username}/?__a=1')
            user.instagram_id = r.json()['user']['id']
            user.save()

        user = self.request.user
        if not user.instagram_id:
            get_instagram_id()
        followers = user.followers.all().values_list('instagram_username', flat=True)
        return {'followers': json.dumps(list(followers))}


class LoadFollowersView(AjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        user = self.request.user
        if user.username == settings.DESECHO8653_USERNAME:
            password = settings.DESECHO8653_PASSWORD
        instagram = Instagram(user.username, password, user.instagram_id)
        followers = instagram.get_followers()
        Follower.objects.filter(user=user).delete()
        for x in followers:
            Follower.objects.create(
                user=user, instagram_id=x['id'], instagram_username=x['username'], name=x['name'], avatar=x['avatar'])

        return self.success()


class LoadMediasView(AjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        user = self.request.user
        if user.username == settings.DESECHO8653_USERNAME:
            password = settings.DESECHO8653_PASSWORD
        instagram = Instagram(user.username, password, user.instagram_id)
        medias = instagram.get_medias()
        Media.objects.filter(user=user).delete()
        for m in medias:
            Media.objects.create(
                user=user,
                instagram_id=m['id'],
                media_type=m['media_type'],
                date=m['date'],
                text=m['text'],
                location=m['location'],
                image=m['image'],
                video=m['video'])

        return self.success()
