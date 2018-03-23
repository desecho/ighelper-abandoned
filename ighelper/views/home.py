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
        likes_count = Like.objects.filter(media__user=user).count()
        if images_count:
            likes_average = likes_count // images_count
        else:
            likes_average = _('not available')
        return {
            'followers_count': followers_count,
            'images_count': images_count,
            'videos_count': videos_count,
            'likes_count': likes_count,
            'likes_average': likes_average,
        }