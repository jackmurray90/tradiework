from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from beatmatcher.models import Interest, DJ
from beatmatcher.translations import tr
from beatmatcher.views.sign_up import (
    SignUpView,
    SignUpSuccessView,
    SignUpVerifyView,
)
from beatmatcher.views.log_in import (
    LogInView,
    LogOutView,
)
from beatmatcher.views.dj import EditDJView, EditDJSuccessView
from beatmatcher.views.booking import NewBookingView, BookingView


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
        if lang not in tr:
            raise Http404
        return render(request, "index.html", {"tr": tr[lang]})


class DJsView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        djs = DJ.objects.all()
        return render(request, "djs.html", {"tr": tr[lang], "djs": djs})


class ClubsView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        clubs = [
            {
                "id": 1,
                "picture": True,
                "name": "Berghain",
                "description": "Berghain is a nightclub in Berlin, Germany. It is named after its location near the border between Kreuzberg and Friedrichshain in Berlin, and is a short walk from Berlin Ostbahnhof main line railway station. Berghain is commonly known as the techno capital of the world.",
            },
            {
                "id": 2,
                "picture": True,
                "name": "Kater Blau",
                "description": "Unpretentious club with a riverside terrace, hosting DJ-led all-night parties with a techno vibe.",
            },
            {
                "id": 3,
                "picture": False,
                "name": "KitKatClub",
                "description": "The KitKatClub is a nightclub in Berlin, opened in March 1994 by Austrian pornographic filmmaker Simon Thaur and his life partner Kirsten Krüger.",
            },
        ]
        return render(request, "clubs.html", {"tr": tr[lang], "clubs": clubs})


class AccountView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        if not request.user.is_authenticated:
            return redirect("log-in", lang=lang)
        return render(request, "account.html", {"tr": tr[lang]})
