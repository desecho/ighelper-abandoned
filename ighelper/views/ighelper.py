import json

from django.shortcuts import get_object_or_404

from ighelper.models import Follower, Like, Media

from .mixins import AjaxView, InstagramAjaxView, TemplateView


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


class LoadFollowersView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        followers = self.instagram.get_followers()
        current_followers = self.user.followers.all()

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
                user=self.user,
                instagram_id=x['id'],
                instagram_username=x['username'],
                name=x['name'],
                avatar=x['avatar'])

        return self.success(followers=self.user.get_followers())


class LoadLikesView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        medias = self.user.medias.all()
        likes = self.instagram.get_likes(medias)
        Like.objects.filter(media__user=self.user).delete()
        for l in likes:
            users = self.user.followers.filter(instagram_id=l['user_instagram_id'])
            if users.exists():
                follower = users[0]
            else:
                follower = None
            Like.objects.create(media=l['media'], follower=follower)

        return self.success(followers=self.user.get_followers())


class UpdateUsersIAmFollowingView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        users_i_am_following = self.instagram.get_users_i_am_following()

        # Reset followed status.
        self.user.followers.update(followed=False)
        followers = self.user.followers.all()

        for u in users_i_am_following:
            # We have a mutual followership.
            followers_found = followers.filter(instagram_id=u['id'])
            if followers_found.exists():
                follower = followers_found[0]
                follower.followed = True
                follower.save()

        return self.success(followers=self.user.get_followers())


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
