from operator import itemgetter

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.signals import user_logged_in
from django.db import models
from django.dispatch import receiver
from django.utils.translation import LANGUAGE_SESSION_KEY

from ighelper.helpers import get_name


def activate_user_language_preference(request, lang):
    request.session[LANGUAGE_SESSION_KEY] = lang


class User(AbstractUser):
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default='en')

    def get_followers(self):
        followers = []
        for f in self.followers.all():
            follower = {
                'id': f.id,
                'elementIdApproved': f'follower-approved{f.id}',
                'elementIdFollowed': f'follower-followed{f.id}',
                'name': str(f),
                'likes_count': f.get_likes_count(),
                'avatar': f.avatar,
                'profile': f.profile,
                'followed': f.followed,
                'approved': f.approved
            }
            followers.append(follower)
        return sorted(followers, key=itemgetter('likes_count'), reverse=True)

    @property
    def videos(self):
        return self.medias.filter(media_type=Media.MEDIA_TYPE_VIDEO)


class ImageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(media_type=Media.MEDIA_TYPE_IMAGE)


class VideoManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(media_type=Media.MEDIA_TYPE_VIDEO)


class Media(models.Model):
    MEDIA_TYPE_IMAGE = 1
    MEDIA_TYPE_VIDEO = 2
    MEDIA_TYPES = (
        (MEDIA_TYPE_IMAGE, 'Image'),
        (MEDIA_TYPE_VIDEO, 'Video'),
    )

    user = models.ForeignKey(User, models.CASCADE, related_name='medias')
    instagram_id = models.CharField(max_length=255)
    date = models.DateTimeField()
    media_type = models.PositiveIntegerField(choices=MEDIA_TYPES)
    caption = models.CharField(max_length=255, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    image = models.URLField(max_length=255)
    image_small = models.URLField(max_length=255)
    video = models.URLField(null=True, blank=True)
    objects = models.Manager()
    images = ImageManager()
    videos = VideoManager()
    likes_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.user} - {self.instagram_id}'

    @staticmethod
    def _replace_single_quotes(text):
        return text.replace("'", '’')

    @property
    def content(self):
        if self.video:
            return self.video
        return self.image

    @property
    def caption_formatted(self):
        return self._replace_single_quotes(self.caption)

    @property
    def location_formatted(self):
        location = self._replace_single_quotes(self.location_name)
        if self.city:
            location += f'; {self.city}'
        return location


class InstagramUser(models.Model):
    instagram_id = models.BigIntegerField()
    username = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    avatar = models.URLField()

    def __str__(self):
        return get_name(self.name, self.username)

    @property
    def profile(self):
        return f'{settings.INSTAGRAM_BASE_URL}/{self.username}/'

    def get_likes_count(self, user):
        return self.likes.filter(media__user=user).count()


class Follower(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='followers')
    instagram_user = models.ForeignKey(InstagramUser, models.CASCADE)
    approved = models.BooleanField(default=False)
    followed = models.BooleanField(default=False)

    @property
    def instagram_id(self):
        return self.instagram_user.instagram_id

    @property
    def avatar(self):
        return self.instagram_user.avatar

    @property
    def profile(self):
        return self.instagram_user.profile

    def __str__(self):
        return str(self.instagram_user)

    def get_likes_count(self):
        return self.instagram_user.get_likes_count(self.user)


class Like(models.Model):
    media = models.ForeignKey(Media, models.CASCADE, related_name='likes')
    instagram_user = models.ForeignKey(InstagramUser, models.CASCADE, related_name='likes')

    def __str__(self):
        return f'{self.media} - {self.instagram_user}'


@receiver(user_logged_in)
def lang(**kwargs):
    activate_user_language_preference(kwargs['request'], kwargs['user'].language)
