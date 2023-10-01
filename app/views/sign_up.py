from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.urls import reverse
from django.conf import settings
from app.util import random_128_bit_string, update_user_lock
from app.models import Settings, SignUp, is_valid_username
from app.translation import tr
from datetime import datetime, timezone, timedelta


class SignUpView(View):
    def get(self, request, lang):
        return render(request, "sign-up.html")

    def post(self, request, lang):
        # Check that a user with that email doesn't already exist
        user = User.objects.filter(email=request.POST["email"]).first()
        if user:
            return render(
                request,
                "sign-up.html",
                {
                    "email": request.POST["email"],
                    "errors": {
                        "email": tr("A user with that email address already exists.", lang),
                    },
                },
            )

        # Create the email verification code
        sign_up = SignUp.objects.create(
            email=request.POST["email"],
            code=random_128_bit_string(),
            expiry=datetime.now(timezone.utc) + timedelta(days=1),
        )

        # Generate the email
        plaintext = get_template(f"emails/sign-up-{lang}.txt")
        html = get_template(f"emails/sign-up-{lang}.html")
        subject = tr(f"Welcome to {settings.SITE_TITLE}", lang)
        from_email = f"no-reply@{request.get_host()}"
        to = sign_up.email
        text_content = plaintext.render(
            {"url": request.build_absolute_uri(reverse("sign-up-verify", kwargs={"lang": lang, "code": sign_up.code}))}
        )
        html_content = html.render(
            {"url": request.build_absolute_uri(reverse("sign-up-verify", kwargs={"lang": lang, "code": sign_up.code}))}
        )

        # Create the email message with the content and send it
        message = EmailMultiAlternatives(subject, text_content, from_email, [to])
        message.attach_alternative(html_content, "text/html")
        message.send()

        return redirect("sign-up-success", lang=lang)


class SignUpSuccessView(View):
    def get(self, request, lang):
        return render(request, "sign-up-success.html")


class SignUpVerifyView(View):
    def get(self, request, lang, code):
        # Verify the sign up code is correct
        sign_up = SignUp.objects.filter(code=code, expiry__gte=datetime.now(timezone.utc)).first()
        if not sign_up:
            return render(
                request,
                "sign-up-verify.html",
                {
                    "error": tr("Invalid verification code.", lang),
                },
            )

        # Verify a user with that email doesn't already exist
        if User.objects.filter(email=sign_up.email).first():
            return render(
                request,
                "sign-up-verify.html",
                {
                    "error": tr("A user with that email address already exists.", lang),
                },
            )

        # Render the template to set password
        return render(request, "sign-up-verify.html")

    def post(self, request, lang, code):
        # Verify the sign up code is correct
        sign_up = SignUp.objects.filter(code=code, expiry__gte=datetime.now(timezone.utc)).first()
        if not sign_up:
            return render(
                request,
                "sign-up-verify.html",
                {
                    "username": request.POST["username"],
                    "error": tr("Invalid verification code.", lang),
                },
            )

        # Verify passwords match
        if not request.POST["password"] == request.POST["password-verify"]:
            return render(
                request,
                "sign-up-verify.html",
                {
                    "username": request.POST["username"],
                    "errors": {
                        "password": "Passwords did not match.",
                    },
                },
            )

        # Verify username is valid
        if not is_valid_username(request.POST["username"]):
            return render(
                request,
                "sign-up-verify.html",
                {
                    "username": request.POST["username"],
                    "errors": {
                        "username": tr(
                            "Invalid username. Must be 150 characters or fewer. Usernames may contain alphanumeric, _, @, +, . and - characters.",
                            lang,
                        ),
                    },
                },
            )

        with update_user_lock:
            # Verify a user with that email doesn't already exist
            if User.objects.filter(email=sign_up.email).first():
                return render(
                    request,
                    "sign-up-verify.html",
                    {
                        "username": request.POST["username"],
                        "error": tr("A user with that email address already exists.", lang),
                    },
                )

            # Verify username is not taken.
            if User.objects.filter(username__iexact=request.POST["username"]).first():
                return render(
                    request,
                    "sign-up-verify.html",
                    {
                        "username": request.POST["username"],
                        "errors": {
                            "username": tr("That username is taken.", lang),
                        },
                    },
                )

            # Create the user and set their password
            user = User.objects.create(username=request.POST["username"], email=sign_up.email)
            user.set_password(request.POST["password"])
            user.save()

        # Create the settings module for the user
        Settings.objects.create(user=user, language=lang)

        # Delete the SignUp object
        sign_up.delete()

        # Log in the user
        login(request, user)

        return redirect("account", lang=lang)
