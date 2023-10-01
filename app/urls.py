from django.urls import path
from app.views import (
    RedirectToLanguageView,
    LogInView,
    SignUpView,
    SignUpSuccessView,
    SignUpVerifyView,
    LogOutView,
    ConceptView,
    WebDevelopmentView,
    AccountView,
)

urlpatterns = [
    # Landing page
    path("", RedirectToLanguageView.as_view(), name="redirect-to-language"),
    path("<lang>/", ConceptView.as_view(), name="index"),
    # Sign up, log in, reset password
    path("<lang>/log-in", LogInView.as_view(), name="log-in"),
    path("<lang>/log-out", LogOutView.as_view(), name="log-out"),
    path("<lang>/sign-up", SignUpView.as_view(), name="sign-up"),
    path("<lang>/sign-up/success", SignUpSuccessView.as_view(), name="sign-up-success"),
    path("<lang>/sign-up/verify/<code>", SignUpVerifyView.as_view(), name="sign-up-verify"),
    # Static Pages
    path("<lang>/concept", ConceptView.as_view(), name="concept"),
    path("<lang>/web-development", WebDevelopmentView.as_view(), name="web-development"),
    # Accounts
    path("<lang>/account", AccountView.as_view(), name="account"),
]
