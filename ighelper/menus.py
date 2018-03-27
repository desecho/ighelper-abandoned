# -*- coding: utf-8 -*-

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem


def is_authenticated(request):
    return request.user.is_authenticated


Menu.add_item('main', MenuItem(_('Home'), reverse('home'), check=is_authenticated))
Menu.add_item('main', MenuItem(_('Medias'), reverse('medias'), check=is_authenticated))
Menu.add_item('main', MenuItem(_('Likes'), reverse('likes'), check=is_authenticated))
Menu.add_item('main', MenuItem(_('Followers'), reverse('followers'), check=is_authenticated))
Menu.add_item('main', MenuItem(_('Following'), reverse('followed'), check=is_authenticated))
