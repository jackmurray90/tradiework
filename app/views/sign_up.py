from datetime import datetime, timezone, timedelta
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from app.util import random_128_bit_string, update_user_lock
from app.models import Language, Settings, SignUp, is_valid_username
from app import forms
from app.emails import send_sign_up_email


USER_ALREADY_EXISTS = "A user with that email address already exists."
INVALID_CODE = "Invalid verification code."


class SignUpForm(forms.Form):
    __title__ = "Sign up"
    email = forms.CharField("Email address", User.email)
    submit = forms.SubmitButton("Sign me up")

    def validate(self, tr):
        # Check that a user with that email doesn't already exist
        user = User.objects.filter(email=self.email).first()
        if user:
            self.add_error(f"email", tr(USER_ALREADY_EXISTS))


class SignUpVerifyForm(forms.Form):
    __title__ = "Set your account details"
    username = forms.CharField("Username", User.username)
    password = forms.PasswordField("Password")
    password_verify = forms.PasswordField("Verify password")
    submit = forms.SubmitButton("Set your account details")

    def validate(self, tr):
        # Verify username is valid
        if not is_valid_username(self.username):
            self.add_error(
                f"username",
                tr("Invalid username. Must be 150 characters or fewer. Usernames may contain alphanumeric, _, @, +, . and - characters."),
            )
        if self.password != self.password_verify:
            self.add_error(tr("Passwords did not match."))


class SignUpView(View):
    def get(self, request, tr):
        form = SignUpForm(request)
        return render(request, f"sign-up.html", {f"form": form})

    def post(self, request, tr):
        form = SignUpForm(request)

        if not form.is_valid:
            return render(request, f"sign-up.html", {f"form": form})

        # Create the email verification code
        sign_up = SignUp.objects.create(
            email=form.email,
            code=random_128_bit_string(),
            expiry=datetime.now(timezone.utc) + timedelta(days=1),
        )

        # Send the sign up email
        send_sign_up_email(request, request.session[f"language"], sign_up.email, sign_up.code)

        return redirect(f"sign-up-success")


class SignUpSuccessView(View):
    def get(self, request, tr):
        return render(request, f"sign-up-success.html")


class SignUpVerifyView(View):
    def get(self, request, tr, code):
        form = SignUpVerifyForm(request)

        # Verify the sign up code is correct
        sign_up = SignUp.objects.filter(code=code, expiry__gte=datetime.now(timezone.utc)).first()
        if not sign_up:
            form.add_error(tr(INVALID_CODE))
            return render(request, f"sign-up-verify.html", {f"form": form})

        # Verify a user with that email doesn't already exist
        if User.objects.filter(email=sign_up.email).first():
            form.add_error(tr(USER_ALREADY_EXISTS))
            return render(request, f"sign-up-verify.html", {f"form": form})

        # Render the template to set password
        return render(request, f"sign-up-verify.html", {f"form": form})

    def post(self, request, tr, code):
        form = SignUpVerifyForm(request)

        if not form.is_valid:
            return render(request, f"sign-up-verify.html", {f"form": form})

        # Verify the sign up code is correct
        sign_up = SignUp.objects.filter(code=code, expiry__gte=datetime.now(timezone.utc)).first()
        if not sign_up:
            form.add_error(tr(INVALID_CODE))
            return render(request, f"sign-up-verify.html", {f"form": form})

        with update_user_lock:
            # Verify a user with that email doesn't already exist
            if User.objects.filter(email=sign_up.email).first():
                form.add_error(tr(USER_ALREADY_EXISTS))
                return render(request, f"sign-up-verify.html", {f"form": form})

            # Verify username is not taken.
            if User.objects.filter(username__iexact=form.username).first():
                form.add_error(f"username", tr("That username is taken."))
                return render(request, f"sign-up-verify.html", {f"form": form})

            # Create the user and set their password
            user = User.objects.create(username=form.username, email=sign_up.email)
            user.set_password(form.password)
            user.save()

        # Save the language in the settings model for the user
        language = Language.objects.get(code=request.session[f"language"])
        settings = user.settings
        settings.language = language
        settings.save()

        # Delete the SignUp object
        sign_up.delete()

        # Log in the user
        login(request, user)

        return redirect(f"account")
