from django.http import HttpResponseRedirect
from app.translation import translations, tr


class TranslationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if "language" not in request.session:
            for language in translations:
                if language in request.LANGUAGE_CODE:
                    break
            else:
                language = "en"
            request.session["language"] = language
        view_kwargs["tr"] = lambda s: tr(s, request.session["language"])
