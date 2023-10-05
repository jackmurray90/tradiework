from django.shortcuts import render, redirect
from django.views import View
from app.models import Language, String


class AdminLanguageView(View):
    def get(self, request, tr):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect(f"log-in")
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
        return render(request, f"admin/languages.html", {f"strings": strings})

    def post(self, request, tr):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect(f"log-in")
        for string in String.objects.filter(language__code=f"en").all():
            for language in Language.objects.all():
                english = string.english
                in_use = string.in_use
                translation = request.POST[f"{language.code}-{string.english}"]
                string = String.objects.filter(language=language, english=english).first()
                if string:
                    string.translation = translation
                    string.save()
                else:
                    String.objects.create(language=language, english=english, translation=translation, in_use=in_use)
        if request.POST.get(f"purge") == f"true":
            String.objects.filter(in_use=False).delete()
        return redirect(f"admin-language")
