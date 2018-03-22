import json

from django.shortcuts import get_object_or_404

from ighelper.models import Follower

from .mixins import AjaxView, InstagramAjaxView, TemplateView


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
            found_followers = current_followers.filter(instagram_id=instagram_id)
            if found_followers.exists():
                follower = found_followers[0]
                follower.name = x['name']
                follower.avatar = x['avatar']
                follower.save()
            else:
                Follower.objects.create(
                    user=self.user,
                    instagram_id=x['id'],
                    instagram_username=x['username'],
                    name=x['name'],
                    avatar=x['avatar'])

        return self.success(followers=self.user.get_followers())


class LoadUsersIAmFollowingView(InstagramAjaxView):
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
            result = self.instagram.follow(follower.instagram_id)
        else:
            result = self.instagram.unfollow(follower.instagram_id)
        if result:

            follower.followed = status
            follower.save()
            return self.success()
        else:
            return self.fail()


class BlockView(InstagramAjaxView):
    def delete(self, *args, **kwargs):  # pylint: disable=unused-argument
        self.get_data()
        follower_id = kwargs['id']
        follower = get_object_or_404(Follower, user=self.request.user, pk=follower_id)
        result = self.instagram.block(follower.instagram_id)
        if result:
            follower.delete()
            return self.success()
        else:
            return self.fail()
