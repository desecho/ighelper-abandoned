from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from ighelper.models import Like, Media

from .mixins import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self):
        user = self.request.user
        followers_count = user.followers.count()
        images_count = Media.images.filter(user=user).count()
        videos_count = Media.videos.filter(user=user).count()
        videos_views_count = Media.videos.filter(user=user).aggregate(count=Sum('views_count'))['count']
        likes_count = Like.objects.filter(media__user=user).count()
        if images_count:
            likes_average = likes_count // images_count
        else:
            likes_average = _('not available')
        if videos_views_count:
            views_average = videos_views_count // videos_count
        else:
            views_average = _('not available')

        if videos_views_count is None:
            videos_views_count = _('not available')

        return {
            'followers_count': followers_count,
            'images_count': images_count,
            'videos_count': videos_count,
            'videos_views_count': videos_views_count,
            'likes_count': likes_count,
            'likes_average': likes_average,
            'views_average': views_average,
        }
