from django import template
from beatmatcher.translations import tr

register = template.Library()


def render_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M")


def translate_status(status, lang):
    print("status is", status)
    return tr[lang][f"Booking{status}"]


register.filter("render_datetime", render_datetime)
register.filter("translate_status", translate_status)
