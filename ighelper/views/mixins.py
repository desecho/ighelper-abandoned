from braces.views import JsonRequestResponseMixin, LoginRequiredMixin
from django.conf import settings
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
        if self.user.username == settings.ADMIN_USERNAME:
            password = settings.ADMIN_PASSWORD
        # instagram = cache.get('instagram')
        # if instagram is None:
        #     instagram = Instagram(self.user.username, password)
        #     cache.set('instagram', instagram)
        # Slow down in attempt to avoid blocking by Instagram / Simulate client behaviour.
        # See https://github.com/mgp25/Instagram-API/wiki/FAQ

        self.instagram = Instagram(settings.ADMIN_INSTAGRAM_ID, self.user.username, password, settings.FAKE_USERNAME,
                                   settings.FAKE_PASSWORD)


class TemplateView(LoginRequiredMixin, TemplateViewOriginal):
    pass


class TemplateAnonymousView(TemplateViewOriginal):
    pass
