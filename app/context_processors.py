from django.conf import settings
from app.models import Language
from django.middleware.csrf import get_token


def globals(request):
    return {
        "SITE_TITLE": settings.SITE_TITLE,
        "SITE_HOST": request.get_host(),
        "SITE_URL": request.build_absolute_uri("/"),
        "SITE_DESCRIPTION": settings.SITE_DESCRIPTION,
        "LANGUAGES": Language.objects.all(),
        "CSRF_TOKEN": get_token(request),
    }
