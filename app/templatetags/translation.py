from django import template
from app.translation import translations, tr as app_tr

register = template.Library()


def with_arg(template, arg):
    return template % arg


@register.simple_tag(takes_context=True)
def tr(context, string, *args):
    language = context.get("language")
    if not language:
        language = context["request"].session["language"]
    if args:
        return app_tr(string, language) % args
    else:
        return app_tr(string, language)


register.filter("with_arg", with_arg)
register.filter("tr", tr)
