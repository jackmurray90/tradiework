from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from beatmatcher.models import Interest
from beatmatcher.translations import tr


class LogInView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        return render(request, "log-in.html", {"tr": tr[lang]})

    def post(self, request, lang):
        if lang not in tr:
            raise Http404

        user = authenticate(
            request, username=request.POST["email"], password=request.POST["password"]
        )
        if user is not None:
            login(request, user)
            return redirect("account", lang=lang)
        else:
            return render(
                request,
                "log-in.html",
                {
                    "tr": tr[lang],
                    "email": request.POST["email"],
                    "error": tr[lang]["Invalidlogin_text"],
                },
            )


class LogOutView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        logout(request)
        return render(request, "log-out.html", {"tr": tr[lang]})
