import json

import requests
from django.conf import settings

from ighelper.instagram import get_followers
from ighelper.models import Follower

from .mixins import AjaxView, TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self):
        followers_number = self.request.user.followers.count()
        return {'followers_number': followers_number}


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
        followers = get_followers(user.username, password, user.instagram_id)
        for x in followers:
            Follower.objects.create(
                user=user, instagram_id=x['id'], instagram_username=x['username'], name=x['name'], avatar=x['avatar'])

        return self.success()
