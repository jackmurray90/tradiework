from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from app.translation import translations
from app.models import Language, String
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
            lang = f"en"
        return redirect(f"index", lang=lang)


class ConceptView(View):
    def get(self, request, lang):
        return render(request, f"concept.html")


class WebDevelopmentView(View):
    def get(self, request, lang):
        return render(request, f"web-development.html")


class AccountView(View):
    def get(self, request, lang):
        if not request.user.is_authenticated:
            return redirect(f"log-in", lang=lang)
        return render(request, f"account.html")


class AdminLanguageView(View):
    def get(self, request, lang):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect(f"log-in", lang=lang)
        strings = []
        for string in String.objects.filter(language__code=f"en").all():
            languages = []
            for language in Language.objects.all():
                languages.append(
                    {
                        f"code": language.code,
                        f"name": language.name,
                        f"translation": String.objects.filter(language=language, english=string.english).first(),
                    }
                )
            strings.append(languages)
        unable_to_generate_code = False
        bracket = chr(123)
        close_bracket = chr(125)
        code = f"translations = {bracket}\n"
        quote = chr(34)
        for language in Language.objects.all():
            code += f"    {quote}{language.code}{quote}: {bracket}\n"
            for string in String.objects.filter(language=language, in_use=True):
                if quote in string.english or quote in string.translation:
                    unable_to_generate_code = True
                code += f"          {quote}{string.english}{quote}: {quote}{string.translation}{quote},\n"
            code += f"    {close_bracket},\n"
        code += f"{close_bracket}\n"
        code += f"def tr(string, lang): return translations.get(lang, {bracket}{close_bracket}).get(string, string)\n"
        if unable_to_generate_code:
            code = None
        return render(request, f"admin-language.html", {f"strings": strings, f"code": code})
