from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _

from ighelper.models import Like, Media

from .mixins import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self):
        user = self.request.user
        followers_count = user.followers.count()
        following_count = user.followed_users.count()
        users_who_are_not_followers_but_liked_media_count = (
            user.get_instagram_user_counters_of_users_who_are_not_followers_but_liked_media().count())

        images_count = Media.images.filter(user=user).count()
        videos_count = Media.videos.filter(user=user).count()
        videos_views_count = Media.videos.filter(user=user).aggregate(count=Sum('views_count'))['count']
        likes = Like.objects.filter(media__user=user)
        likes_count = likes.count()
        followers_instagram_users = user.followers.values('instagram_user')
        likes_followers_count = likes.filter(instagram_user__in=followers_instagram_users).count()
        likes_followers_percentage = round(likes_followers_count / likes_count * 100)
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
            'following_count': following_count,
            'users_who_are_not_followers_but_liked_media_count': users_who_are_not_followers_but_liked_media_count,
            'images_count': images_count,
            'videos_count': videos_count,
            'videos_views_count': videos_views_count,
            'likes_count': likes_count,
            'likes_followers_percentage': likes_followers_percentage,
            'likes_average': likes_average,
            'views_average': views_average,
        }
