from django import template
from app.translation import translations, tr

register = template.Library()


def with_arg(template, arg):
    return template % arg


register.filter("with_arg", with_arg)
register.filter("tr", tr)
