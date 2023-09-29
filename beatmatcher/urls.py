"""beatmatcher URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from beatmatcher.views import (
    LandingPageView,
    InterestView,
    ThanksView,
    IndexView,
    LogInView,
    SignUpView,
    SignUpSuccessView,
    SignUpVerifyView,
    SignUpVerifySuccessView,
    LogOutView,
    DJsView,
    ClubsView,
    BookView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", LandingPageView.as_view(), name="landing-page"),
    path("<lang>", InterestView.as_view(), name="interest"),
    path("<lang>/thanks", ThanksView.as_view(), name="thanks"),
    path("<lang>/index", IndexView.as_view(), name="index"),
    path("<lang>/log-in", LogInView.as_view(), name="log-in"),
    path("<lang>/log-out", LogOutView.as_view(), name="log-out"),
    path("<lang>/sign-up", SignUpView.as_view(), name="sign-up"),
    path("<lang>/sign-up/success", SignUpSuccessView.as_view(), name="sign-up-success"),
    path(
        "<lang>/sign-up/verify/success",
        SignUpVerifySuccessView.as_view(),
        name="sign-up-verify-success",
    ),
    path(
        "<lang>/sign-up/verify/<code>",
        SignUpVerifyView.as_view(),
        name="sign-up-verify",
    ),
    path("<lang>/djs", DJsView.as_view(), name="djs"),
    path("<lang>/clubs", ClubsView.as_view(), name="clubs"),
    path("<lang>/book/<dj_username>", BookView.as_view(), name="book"),
]
