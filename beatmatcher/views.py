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
        if lang not in tr:
            raise Http404
        return render(request, "index.html", {"tr": tr[lang]})


class LoginView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        return render(request, "login.html", {"tr": tr[lang]})


class SignupView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        return render(request, "signup.html", {"tr": tr[lang]})


class DJsView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        djs = [
            {
                "id": 2,
                "picture": True,
                "name": "Ben Klock",
                "description": "German DJ and producer Ben Klock is a renowned advocate of the trance-inducing minimal techno with which Berlin's Berghain club and its Ostgut Ton imprint are synonymous. Klock was raised in Berlin and began DJing in the mid '90s at the illegal rave scene which blossomed after the fall of the Wall.",
                "styles": ["techno"],
                "in_house": False,
                "booking_url": "https://circle-booking.com/",
                "soundcloud_url": "https://soundcloud.com/ben-klock",
            },
            {
                "id": 1,
                "picture": True,
                "username": "postmodern",
                "name": "Postmodern",
                "description": "Postmodern is a DJ in Berlin specializing in techno and house music.",
                "styles": ["techno", "house"],
                "in_house": True,
                "soundcloud_url": "https://soundcloud.com/postmoderndj",
                "rate": 300,
            },
        ]
        return render(request, "djs.html", {"tr": tr[lang], "djs": djs})


class BookView(View):
    def get(self, request, lang, dj_username):
        if lang not in tr:
            raise Http404
        dj = {
            "id": 1,
            "picture": True,
            "name": "Postmodern",
            "description": "Postmodern is a DJ in Berlin specializing in techno and house music.",
            "styles": ["techno", "house"],
            "in_house": True,
            "soundcloud_url": "https://soundcloud.com/postmoderndj",
            "rate": 300,
        }
        return render(request, "book.html", {"tr": tr[lang], "dj": dj})


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
