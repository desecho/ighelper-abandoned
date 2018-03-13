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
        if self.user.username == settings.DESECHO8653_USERNAME:
            password = settings.DESECHO8653_PASSWORD
        self.instagram = Instagram(self.user.username, password)


class TemplateView(LoginRequiredMixin, TemplateViewOriginal):
    pass


class TemplateAnonymousView(TemplateViewOriginal):
    pass
