import operator
from collections import defaultdict

from ighelper.models import Like

from .mixins import TemplateView


class LikesView(TemplateView):
    template_name = 'likes.html'

    def get_context_data(self):
        user = self.request.user
        followers = user.followers.values_list('instagram_user__pk', flat=True).distinct()
        likes = Like.objects.filter(media__user=user).exclude(instagram_user__in=followers)
        users_likes_count = defaultdict(int)
        for like in likes:
            instagram_user = like.instagram_user
            users_likes_count[instagram_user] += 1

        users_likes_count = sorted(users_likes_count.items(), key=operator.itemgetter(1), reverse=True)
        return {'users_likes_count': users_likes_count}
