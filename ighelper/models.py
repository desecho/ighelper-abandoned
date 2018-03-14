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
                'elementId': f'follower{f.id}',
                'name': str(f),
                'number_likes': f.get_number_likes(self),
                'avatar': f.avatar,
                'profile': f.profile,
                'followed': f.followed,
                'approved': f.approved
            }
            followers.append(follower)
        return sorted(followers, key=itemgetter('number_likes'), reverse=True)


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
    text = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    image = models.URLField(max_length=255)
    video = models.URLField(null=True, blank=True)
    images = ImageManager()
    videos = VideoManager()
    objects = models.Manager()

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return f'{self.user} - {self.instagram_id}'

    @property
    def content(self):
        if self.video:
            return self.video
        return self.image


class Follower(models.Model):
    user = models.ForeignKey(User, models.CASCADE, related_name='followers')
    instagram_id = models.CharField(max_length=255)
    instagram_username = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True)
    avatar = models.URLField()
    approved = models.BooleanField(default=False)
    followed = models.BooleanField(default=False)

    def __str__(self):
        return get_name(self.name, self.instagram_username)

    @property
    def profile(self):
        return f'{settings.INSTAGRAM_BASE_URL}/{self.instagram_username}/'

    def get_number_likes(self, user):
        return self.likes.filter(media__user=user).count()


class Like(models.Model):
    media = models.ForeignKey(Media, models.CASCADE, related_name='likes')
    follower = models.ForeignKey(Follower, models.CASCADE, related_name='likes', null=True, blank=True)

    def __str__(self):
        return f'{self.media} - {self.follower}'


@receiver(user_logged_in)
def lang(**kwargs):
    activate_user_language_preference(kwargs['request'], kwargs['user'].language)
