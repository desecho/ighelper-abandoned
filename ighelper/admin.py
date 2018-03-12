from django.contrib import admin

from .models import Follower, Like, Media, User

admin.site.register(User)
admin.site.register(Media)
admin.site.register(Follower)
admin.site.register(Like)
