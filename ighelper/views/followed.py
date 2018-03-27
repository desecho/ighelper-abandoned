import json
from operator import itemgetter

from django.shortcuts import get_object_or_404

from ighelper.models import Followed, InstagramUser

from .mixins import AjaxView, InstagramAjaxView, TemplateView


def get_followed_users_excluding_followers(user):
    followers = user.followers.values_list('instagram_user', flat=True)
    followed_users = user.followed_users.exclude(instagram_user__in=followers)
    followed_users_excluding_followers = []
    for followed_user in followed_users:
        instagram_user = followed_user.instagram_user
        followed_user_excluding_followers = {
            'id': followed_user.pk,
            'elementIdConfirmed': f'user-confirmed{followed_user.pk}',
            'confirmed': followed_user.confirmed,
            'profile': instagram_user.profile,
            'avatar': instagram_user.avatar,
            'name': str(followed_user),
        }
        followed_users_excluding_followers.append(followed_user_excluding_followers)

    return sorted(followed_users_excluding_followers, key=itemgetter('name'))


class FollowedView(TemplateView):
    template_name = 'followed.html'

    def get_context_data(self):
        return {'followed': json.dumps(get_followed_users_excluding_followers(self.request.user))}


class LoadFollowedView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        followed_users_instagram = self.instagram.get_followed()
        self.update_cache()
        # Reset followed status.
        self.user.followers.update(followed=False)
        followers = self.user.followers.all()
        followed_users_instagram_ids = [u['instagram_id'] for u in followed_users_instagram]
        self.user.followed_users.exclude(instagram_user__instagram_id__in=followed_users_instagram_ids).delete()
        for followed_user_instagram in followed_users_instagram:
            users_found = InstagramUser.objects.filter(instagram_id=followed_user_instagram['instagram_id'])
            if users_found.exists():
                users_found.update(**followed_user_instagram)
                instagram_user = users_found[0]
            else:
                instagram_user = InstagramUser.objects.create(**followed_user_instagram)

            Followed.objects.get_or_create(user=self.user, instagram_user=instagram_user)

            # We have a mutual followership.
            followers_found = followers.filter(instagram_user=instagram_user)
            if followers_found.exists():
                follower = followers_found[0]
                follower.followed = True
                follower.save()

        return self.success(followed=get_followed_users_excluding_followers(self.user))


class SetConfirmedStatusView(AjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        try:
            status = json.loads(self.request.PUT['status'])
        except KeyError:
            return self.render_bad_request_response()
        user_id = kwargs['id']
        followed_user = get_object_or_404(Followed, user=self.request.user, pk=user_id)
        followed_user.confirmed = status
        followed_user.save()
        return self.success()


class UnfollowView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        user_id = kwargs['id']
        followed_user = get_object_or_404(Followed, user=self.request.user, pk=user_id)
        self.instagram.unfollow(followed_user.instagram_id)
        self.update_cache()
        followed_user.delete()
        return self.success()
