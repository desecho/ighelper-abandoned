"""URL Configuration."""
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.views import login
from django.urls import path, re_path
from django.views.i18n import JavaScriptCatalog

from ighelper.views.followed import (
    FollowedView,
    LoadFollowedView,
    SetConfirmedStatusView,
    UnfollowView,
)
from ighelper.views.followers import (
    BlockView,
    FollowersView,
    LoadFollowersView,
    SetApprovedStatusView,
    SetFollowedStatusView,
)
from ighelper.views.home import HomeView
from ighelper.views.likes import LikesView, LoadLikesView
from ighelper.views.medias import (
    CaptionUpdateView,
    LoadMediasView,
    LoadViewsView,
    MediasView,
    MediaView,
    UpdateMediasView,
)
from ighelper.views.user import (
    PreferencesView,
    SavePreferencesView,
    logout_view,
)

admin.autodiscover()

urlpatterns = []

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

urlpatterns += [
    # User
    path('login/', login, {'template_name': 'user/login.html'}, name='login'),
    path('logout/', logout_view, name='logout'),

    # Preferences
    path('preferences/', PreferencesView.as_view(), name='preferences'),
    path('save-preferences/', SavePreferencesView.as_view(), name='save_preferences'),

    # Services
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(packages=('ighelper', ), domain='djangojs'), name='javascript-catalog'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('rosetta/', include('rosetta.urls')),
    # -------------------------------------------------------------------------------------------
    path('', HomeView.as_view(), name='home'),
    path('medias/', MediasView.as_view(), name='medias'),
    path('likes/', LikesView.as_view(), name='likes'),
    re_path(r'medias/(?P<id>\d+)/caption/', CaptionUpdateView.as_view(), name='media'),
    re_path(r'medias/(?P<id>\d+)/', MediaView.as_view(), name='media'),
    path('medias/load/likes/', LoadLikesView.as_view(), name='load_likes'),
    path('medias/load/views/', LoadViewsView.as_view(), name='load_views'),
    path('medias/load/', LoadMediasView.as_view(), name='load_medias'),
    path('medias/update/', UpdateMediasView.as_view(), name='update_medias'),
    path('followers/', FollowersView.as_view(), name='followers'),
    path('followers/load/', LoadFollowersView.as_view(), name='load_followers'),
    re_path(r'followers/(?P<id>\d+)/block/', BlockView.as_view(), name='block'),
    re_path(
        r'followers/(?P<id>\d+)/set-approved-status/', SetApprovedStatusView.as_view(), name='set_approved_status'),
    re_path(
        r'followers/(?P<id>\d+)/set-followed-status/', SetFollowedStatusView.as_view(), name='set_followed_status'),
    path('followed/', FollowedView.as_view(), name='followed'),
    path('followed/load/', LoadFollowedView.as_view(), name='load_followed'),
    re_path(r'followed/(?P<id>\d+)/unfollow/', UnfollowView.as_view(), name='unfollow'),
    re_path(
        r'followed/(?P<id>\d+)/set-confirmed-status/', SetConfirmedStatusView.as_view(), name='set_confirmed_status'),
]
