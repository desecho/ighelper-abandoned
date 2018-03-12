from django.contrib.auth import logout
from django.shortcuts import redirect

from ighelper.models import activate_user_language_preference

from .mixins import AjaxView, TemplateView


def logout_view(request):
    logout(request)
    return redirect('/')


class PreferencesView(TemplateView):
    template_name = 'user/preferences.html'


class SavePreferencesView(AjaxView):
    def post(self, request):
        try:
            language = request.POST['language']
        except KeyError:
            return self.render_bad_request_response()

        user = request.user
        user.language = language
        user.save()
        activate_user_language_preference(request, language)
        return self.success()
