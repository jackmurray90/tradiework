from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from app.translation import translations
from app.views.sign_up import (
    SignUpView,
    SignUpSuccessView,
    SignUpVerifyView,
)
from app.views.log_in import (
    LogInView,
    LogOutView,
)


class RedirectToLanguageView(View):
    def get(self, request):
        for lang in translations:
            if lang in request.LANGUAGE_CODE:
                break
        else:
            lang = "en"
        return redirect("index", lang=lang)


class ConceptView(View):
    def get(self, request, lang):
        return render(request, "concept.html")


class WebDevelopmentView(View):
    def get(self, request, lang):
        return render(request, "web-development.html")


class AccountView(View):
    def get(self, request, lang):
        if not request.user.is_authenticated:
            return redirect("log-in", lang=lang)
        return render(request, "account.html")
