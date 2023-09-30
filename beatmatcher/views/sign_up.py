from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.urls import reverse
from beatmatcher.util import random_128_bit_string, update_user_lock
from beatmatcher.models import Settings, SignUp, is_valid_username
from beatmatcher.translations import tr
from datetime import datetime, timezone, timedelta


class SignUpView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        return render(request, "sign-up.html", {"tr": tr[lang]})

    def post(self, request, lang):
        if lang not in tr:
            raise Http404

        # Check that a user with that email doesn't already exist
        user = User.objects.filter(email=request.POST["email"]).first()
        if user:
            return render(
                request,
                "sign-up.html",
                {
                    "tr": tr[lang],
                    "email": request.POST["email"],
                    "errors": {
                        "email": tr[lang]["Auserwiththatemailaddressalreadyexists"],
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
        plaintext = get_template(f"sign-up-email-{lang}.txt")
        html = get_template(f"sign-up-email-{lang}.html")
        subject = tr[lang]["WelcometoBeatmatcher"]
        from_email = "no-reply@beatmatcher.org"
        to = sign_up.email
        text_content = plaintext.render(
            {
                "url": request.build_absolute_uri(
                    reverse(
                        "sign-up-verify", kwargs={"lang": lang, "code": sign_up.code}
                    )
                )
            }
        )
        html_content = html.render(
            {
                "url": request.build_absolute_uri(
                    reverse(
                        "sign-up-verify", kwargs={"lang": lang, "code": sign_up.code}
                    )
                )
            }
        )

        # Create the email message with the content and send it
        message = EmailMultiAlternatives(subject, text_content, from_email, [to])
        message.attach_alternative(html_content, "text/html")
        message.send()

        return redirect("sign-up-success", lang=lang)


class SignUpSuccessView(View):
    def get(self, request, lang):
        if lang not in tr:
            raise Http404
        return render(request, "sign-up-success.html", {"tr": tr[lang]})


class SignUpVerifyView(View):
    def get(self, request, lang, code):
        if lang not in tr:
            raise Http404

        # Verify the sign up code is correct
        sign_up = SignUp.objects.filter(
            code=code, expiry__gte=datetime.now(timezone.utc)
        ).first()
        if not sign_up:
            return render(
                request,
                "sign-up-verify.html",
                {
                    "tr": tr[lang],
                    "error": tr[lang]["Invalidverificationcode"],
                },
            )

        # Verify a user with that email doesn't already exist
        if User.objects.filter(email=sign_up.email).first():
            return render(
                request,
                "sign-up-verify.html",
                {
                    "tr": tr[lang],
                    "error": tr[lang]["Auserwiththatemailaddressalreadyexists"],
                },
            )

        # Render the template to set password
        return render(request, "sign-up-verify.html", {"tr": tr[lang]})

    def post(self, request, lang, code):
        if lang not in tr:
            raise Http404

        # Verify the sign up code is correct
        sign_up = SignUp.objects.filter(
            code=code, expiry__gte=datetime.now(timezone.utc)
        ).first()
        if not sign_up:
            return render(
                request,
                "sign-up-verify.html",
                {
                    "tr": tr[lang],
                    "username": request.POST["username"],
                    "error": tr[lang]["Invalidverificationcode"],
                },
            )

        # Verify passwords match
        if not request.POST["password"] == request.POST["password-verify"]:
            return render(
                request,
                "sign-up-verify.html",
                {
                    "tr": tr[lang],
                    "username": request.POST["username"],
                    "errors": {
                        "password": tr[lang]["Passwordsdidnotmatch"],
                    },
                },
            )

        # Verify username is valid
        if not is_valid_username(request.POST["username"]):
            return render(
                request,
                "sign-up-verify.html",
                {
                    "tr": tr[lang],
                    "username": request.POST["username"],
                    "errors": {
                        "username": tr[lang]["Invalidusername_text"],
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
                        "tr": tr[lang],
                        "username": request.POST["username"],
                        "error": tr[lang]["Auserwiththatemailaddressalreadyexists"],
                    },
                )

            # Verify username is not taken.
            if User.objects.filter(username__iexact=request.POST["username"]).first():
                return render(
                    request,
                    "sign-up-verify.html",
                    {
                        "tr": tr[lang],
                        "username": request.POST["username"],
                        "errors": {
                            "username": tr[lang]["Thatusernameistaken"],
                        },
                    },
                )

            # Create the user and set their password
            user = User.objects.create(
                username=request.POST["username"], email=sign_up.email
            )
            user.set_password(request.POST["password"])
            user.save()

        # Create the settings module for the user
        Settings.objects.create(user=user)

        # Delete the SignUp object
        sign_up.delete()

        # Log in the user
        login(request, user)

        return redirect("account", lang=lang)
