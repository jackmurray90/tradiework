from django.conf import settings


def globals(request):
    return {
        "SITE_TITLE": settings.SITE_TITLE,
        "SITE_HOST": request.get_host(),
        "SITE_URL": request.build_absolute_uri("/"),
        "SITE_DESCRIPTION": settings.SITE_DESCRIPTION,
        "lang": request.path[1:3],
    }
