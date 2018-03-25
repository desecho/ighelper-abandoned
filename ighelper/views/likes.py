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
        user_likes_counts = defaultdict(int)
        for like in likes:
            instagram_user = like.instagram_user
            user_likes_counts[instagram_user] += 1

        user_likes_counts = sorted(user_likes_counts.items(), key=operator.itemgetter(1), reverse=True)
        return {'user_likes_counts': user_likes_counts}
