from braces.views import JsonRequestResponseMixin, LoginRequiredMixin
from django.conf import settings
from django.core.cache import cache
from django.views.generic import TemplateView as TemplateViewOriginal, View

from ighelper.instagram import Instagram


class AjaxAnonymousView(JsonRequestResponseMixin, View):
    MESSAGE_ERROR = 'error'
    MESSAGE_INFO = 'info'
    MESSAGE_WARNING = 'warning'
    MESSAGE_SUCCESS = 'success'

    def success(self, **kwargs):
        response = {'status': 'success'}
        response.update(kwargs)
        return self.render_json_response(response)

    def fail(self, message=None, message_type=MESSAGE_ERROR, **kwargs):
        response = {'status': 'fail', 'message': message, 'messageType': message_type}
        response.update(kwargs)
        return self.render_json_response(response)


class AjaxView(LoginRequiredMixin, AjaxAnonymousView):
    raise_exception = True


class InstagramAjaxView(AjaxView):
    user = None
    instagram = None

    def get_data(self):
        self.user = self.request.user
        username = self.user.username
        if username == settings.ADMIN_USERNAME:
            password = settings.ADMIN_PASSWORD

        instagram = cache.get('instagram')
        if instagram is None:
            instagram = Instagram(settings.ADMIN_INSTAGRAM_ID, username, password, settings.FAKE_USERNAME,
                                  settings.FAKE_PASSWORD)
        self.instagram = instagram

    def update_cache(self):
        cache.set('instagram', self.instagram)

    def update_mutual(self):
        following_instagram_users_ids = self.user.followed_users.values_list('instagram_user', flat=True)
        followers = self.user.followers.all()
        followers.update(followed=False)
        followers.filter(instagram_user__pk__in=following_instagram_users_ids).update(followed=True)


class TemplateView(LoginRequiredMixin, TemplateViewOriginal):
    pass


class TemplateAnonymousView(TemplateViewOriginal):
    pass
