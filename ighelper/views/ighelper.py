import json

from django.conf import settings
from django.shortcuts import get_object_or_404

from ighelper.instagram import Instagram
from ighelper.models import Follower, Like, Media

from .mixins import AjaxView, TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self):
        user = self.request.user
        followers_number = user.followers.count()
        images_number = Media.images.filter(user=user).count()
        videos_number = Media.videos.filter(user=user).count()
        likes_number = Like.objects.filter(media__user=user).count()
        return {
            'followers_number': followers_number,
            'images_number': images_number,
            'videos_number': videos_number,
            'likes_number': likes_number
        }


class FollowersView(TemplateView):
    template_name = 'followers.html'

    def get_context_data(self):
        return {'followers': json.dumps(self.request.user.get_followers())}


class LoadFollowersView(AjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        user = self.request.user
        if user.username == settings.DESECHO8653_USERNAME:
            password = settings.DESECHO8653_PASSWORD
        instagram = Instagram(user.username, password)
        followers = instagram.get_followers()
        user.followers.all().delete()
        for x in followers:
            Follower.objects.create(
                user=user, instagram_id=x['id'], instagram_username=x['username'], name=x['name'], avatar=x['avatar'])

        return self.success(followers=user.get_followers())


class UpdateFollowersView(AjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        user = self.request.user
        if user.username == settings.DESECHO8653_USERNAME:
            password = settings.DESECHO8653_PASSWORD
        instagram = Instagram(user.username, password)
        followers = instagram.get_followers()
        current_followers = user.followers.all()

        # Remove followers which have been deleted / have unfollowed
        followers_ids = [x['id'] for x in followers]
        for follower in current_followers:
            if follower.instagram_id not in followers_ids:
                follower.delete()

        for x in followers:
            instagram_id = x['id']
            if current_followers.filter(instagram_id=instagram_id).exists():
                continue
            Follower.objects.create(
                user=user, instagram_id=x['id'], instagram_username=x['username'], name=x['name'], avatar=x['avatar'])

        return self.success(followers=user.get_followers())


class LoadMediasView(AjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        user = self.request.user
        if user.username == settings.DESECHO8653_USERNAME:
            password = settings.DESECHO8653_PASSWORD
        instagram = Instagram(user.username, password)
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


class LoadLikesView(AjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        user = self.request.user
        if user.username == settings.DESECHO8653_USERNAME:
            password = settings.DESECHO8653_PASSWORD
        instagram = Instagram(user.username, password)
        medias = user.medias.all()
        likes = instagram.get_likes(medias)
        Like.objects.filter(media__user=user).delete()
        for l in likes:
            users = user.followers.filter(instagram_id=l['user_instagram_id'])
            if users.exists():
                follower = users[0]
            else:
                follower = None
            Like.objects.create(media=l['media'], follower=follower)

        return self.success()


class UpdateUsersIAmFollowingView(AjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        user = self.request.user
        if user.username == settings.DESECHO8653_USERNAME:
            password = settings.DESECHO8653_PASSWORD
        instagram = Instagram(user.username, password)
        users_i_am_following = instagram.get_users_i_am_following()

        # Reset followed status.
        user.followers.update(followed=False)
        followers = user.followers.all()

        for u in users_i_am_following:
            # We have a mutual followership.
            followers_found = followers.filter(instagram_id=u['id'])
            if followers_found.exists():
                follower = followers_found[0]
                follower.followed = True
                follower.save()

        return self.success(followers=user.get_followers())


class SetApprovedStatusView(AjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        try:
            status = json.loads(self.request.PUT['status'])
        except KeyError:
            return self.render_bad_request_response()

        follower = get_object_or_404(Follower, user=self.request.user, id=kwargs['id'])
        follower.approved = status
        follower.save()
        return self.success()
