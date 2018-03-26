from django.contrib import admin

from .models import Followed, Follower, InstagramUser, Like, Media, User

admin.site.register(User)
admin.site.register(InstagramUser)
admin.site.register(Follower)
admin.site.register(Followed)
admin.site.register(Media)
admin.site.register(Like)
