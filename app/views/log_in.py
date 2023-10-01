from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from app.translation import tr


class LogInView(View):
    def get(self, request, lang):
        return render(request, "log-in.html")

    def post(self, request, lang):
        user = authenticate(request, username=request.POST["email"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            return redirect("account", lang=lang)
        else:
            return render(
                request,
                "log-in.html",
                {
                    "email": request.POST["email"],
                    "error": tr("Invalid email address or password.", lang),
                },
            )


class LogOutView(View):
    def get(self, request, lang):
        logout(request)
        return render(request, "log-out.html")
