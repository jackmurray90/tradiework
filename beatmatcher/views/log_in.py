from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.contrib.auth import login, logout
from beatmatcher.models import Interest
from beatmatcher.translations import tr


class LogInView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        return render(request, "log-in.html", {"tr": tr[lang]})


class LogOutView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        logout(request)
        return render(request, "log-out.html", {"tr": tr[lang]})
