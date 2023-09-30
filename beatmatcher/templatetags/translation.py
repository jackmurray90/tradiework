from django import template

register = template.Library()

def with_arg(template, arg):
    return template % arg

register.filter("with_arg", with_arg)
