from django import template

register = template.Library()


def render_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M")


register.filter("render_datetime", render_datetime)
