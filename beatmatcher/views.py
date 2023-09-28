from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from beatmatcher.models import Interest
from beatmatcher.translations import tr


class LandingPageView(View):
    def get(self, request):
        lang = "de" if "de" in request.LANGUAGE_CODE else "en"
        return redirect("interest", lang=lang)


class InterestView(View):
    def get(self, request, lang):
        if lang not in ["en", "de"]:
            raise Http404
        return render(request, f"{lang}.html")

    def post(self, request, lang):
        if lang not in ["en", "de"]:
            raise Http404
        try:
            Interest.objects.create(
                type=request.POST["type"],
                name=request.POST["name"],
                email=request.POST["email"],
            )
        finally:
            return redirect("thanks", lang=lang)


class ThanksView(View):
    def get(self, request, lang):
        if lang not in ["en", "de"]:
            raise Http404
        return render(request, f"thanks_{lang}.html")


class IndexView(View):
    def get(self, request, lang):
        if lang not in tr: raise Http404
        return render(request, "index.html", {"tr": tr[lang]})
