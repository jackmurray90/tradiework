from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views import View
from app.translation import tr, register
from app.models import User
from app import forms


LOG_IN = register("Log in")
EMAIL = register("Email")
PASSWORD = register("Password")
LOG_ME_IN = register("Log me in")
INVALID_LOG_IN = register("Invalid email address or password.")


class LogInForm(forms.Form):
    __title__ = LOG_IN
    email = forms.CharField(EMAIL, User.email)
    password = forms.PasswordField(PASSWORD)
    submit = forms.SubmitButton(LOG_ME_IN)


class LogInView(View):
    def get(self, request, lang):
        form = LogInForm(request)
        return render(request, "log-in.html", {"form": form})

    def post(self, request, lang):
        form = LogInForm(request)
        if not form.is_valid:
            return render(request, "log-in.html", {"form": form})

        user = authenticate(request, username=form.email, password=form.password)
        if user is None:
            form.add_error(tr(INVALID_LOG_IN, lang))
            return render(request, "log-in.html", {"form": form})

        login(request, user)
        return redirect("account", lang=lang)


class LogOutView(View):
    def get(self, request, lang):
        logout(request)
        return render(request, "log-out.html")
