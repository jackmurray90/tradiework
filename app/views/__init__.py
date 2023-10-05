from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponse
from app.translation import translations
from django.views import View
from app.models import Language
from app.views.sign_up import (
    SignUpView,
    SignUpSuccessView,
    SignUpVerifyView,
)
from app.views.log_in import (
    LogInView,
    LogOutView,
)
from app.views.admin import AdminLanguageView


class ConceptView(View):
    def get(self, request, tr):
        return render(request, f"concept.html")


class AccountView(View):
    def get(self, request, tr):
        if not request.user.is_authenticated:
            return redirect(f"log-in")
        return render(request, f"account.html")


class ChangeLanguageView(View):
    def post(self, request, tr):
        language = request.POST[f"language"]
        if language not in translations:
            return HttpResponseBadRequest()
        request.session[f"language"] = language
        if request.user.is_authenticated:
            settings = request.user.settings
            settings.language = Language.objects.get(code=language)
            settings.save()
        return HttpResponse()
