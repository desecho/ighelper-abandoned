import json
from operator import itemgetter

from django.shortcuts import get_object_or_404

from ighelper.models import Follower, InstagramUser

from .mixins import AjaxView, InstagramAjaxView, TemplateView


def get_followers(user):
    followers = []
    for f in user.followers.all():
        follower = {
            'id': f.pk,
            'elementIdApproved': f'follower-approved{f.pk}',
            'elementIdFollowed': f'follower-followed{f.pk}',
            'name': str(f),
            'likes_count': f.get_likes_count(),
            'avatar': f.avatar,
            'profile': f.profile,
            'followed': f.followed,
            'approved': f.approved
        }
        followers.append(follower)
    return sorted(followers, key=itemgetter('likes_count'), reverse=True)


class FollowersView(TemplateView):
    template_name = 'followers.html'

    def get_context_data(self):
        return {'followers': json.dumps(get_followers(self.request.user))}


class LoadFollowersView(InstagramAjaxView):
    def post(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        instagram_followers = self.instagram.get_followers()
        self.update_cache()
        current_followers = self.user.followers.all()

        # Remove followers which have been deleted / have unfollowed
        followers_instagram_ids = [x['instagram_id'] for x in instagram_followers]
        for follower in current_followers:
            if follower.instagram_id not in followers_instagram_ids:
                follower.delete()

        for instagram_follower in instagram_followers:
            instagram_users = InstagramUser.objects.filter(instagram_id=instagram_follower['instagram_id'])
            if instagram_users.exists():
                instagram_users.update(**instagram_follower)
                instagram_user = instagram_users[0]
            else:
                instagram_user = InstagramUser.objects.create(**instagram_follower)

            if not current_followers.filter(instagram_user=instagram_user).exists():
                Follower.objects.create(user=self.user, instagram_user=instagram_user)

        self.update_mutual()
        return self.success(followers=get_followers(self.user))


class SetApprovedStatusView(AjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        try:
            status = json.loads(self.request.PUT['status'])
        except KeyError:
            return self.render_bad_request_response()

        follower = get_object_or_404(Follower, user=self.request.user, pk=kwargs['id'])
        follower.approved = status
        follower.save()
        return self.success()


class SetFollowedStatusView(InstagramAjaxView):
    def put(self, *args, **kwargs):  # pylint: disable=unused-argument
        try:
            status = json.loads(self.request.PUT['status'])
        except KeyError:
            return self.render_bad_request_response()

        self.get_data()
        follower_id = kwargs['id']
        follower = get_object_or_404(Follower, user=self.request.user, pk=follower_id)
        if status:
            self.instagram.follow(follower.instagram_id)
        else:
            self.instagram.unfollow(follower.instagram_id)
        self.update_cache()
        follower.followed = status
        follower.save()
        return self.success()


class BlockView(InstagramAjaxView):
    def delete(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        follower_id = kwargs['id']
        follower = get_object_or_404(Follower, user=self.request.user, pk=follower_id)
        self.instagram.block(follower.instagram_id)
        self.update_cache()
        follower.delete()
        return self.success()
