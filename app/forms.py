from django.utils.safestring import mark_safe
from django.template import loader
from app.translation import tr
from app.util import random_128_bit_string
from copy import copy


class Element:
    # Translate all non-error strings required to be translated for this
    # element.
    def translate(self, lang):
        self.label = tr(self.label, lang)


class Field(Element):
    IS_REQUIRED = "%s is required."

    def set_name(self, name):
        self.name = name

    def set_value(self, value):
        self.value = value

    def set_error(self, error):
        self.error = error


class CharField(Field):
    type = f"text"

    def __init__(self, label, model_field=None, required=True):
        self.label = label
        self.max_length = model_field.field.max_length if model_field else None
        self.required = required

    def validate(self, lang):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED, lang) % tr(self.label, lang)
        if self.max_length is not None and len(self.value) > self.max_length:
            return tr("%s can be a maximum of %s characters.", lang) % (tr(self.label, lang), self.max_length)


class PasswordField(Field):
    type = f"password"

    def __init__(self, label, required=True):
        self.label = label
        self.required = required

    def validate(self, lang):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED, lang) % tr(self.label, lang)


class TextField(Field):
    type = f"textarea"

    def __init__(self, label, required=True):
        self.label = label
        self.required = required

    def validate(self, lang):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED, lang) % tr(self.label, lang)


class FileField(Field):
    type = f"file"

    def __init__(self, label, button_text, information_text=None, max_size=None, required=True):
        self.label = label
        self.button_text = button_text
        self.information_text = information_text
        self.max_size = max_size
        self.required = required

    def translate(self, lang):
        self.label = tr(self.label, lang)
        self.button_text = tr(self.button_text, lang)
        if self.information_text:
            self.information_text = tr(self.information_text, lang)

    def max_size_readable(self):
        if self.max_size < 1024:
            return f"{self.max_size} bytes"
        if self.max_size < 1024 * 1024:
            return f"{self.max_size/1024} KB"
        if self.max_size < 1024 * 1024 * 1024:
            return f"{self.max_size/(1024*1024)} MB"
        return f"{self.max_size/(1024*1024*1024)} GB"

    def validate(self, lang):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED, lang) % tr(self.label, lang)
        if self.max_size and self.value and self.value.size > self.max_size:
            return tr("%s is too large. Maximum file size is %s", lang) % (tr(self.label, lang), self.max_size_readable())


class IntegerField(Field):
    type = f"text"

    def __init__(self, label, positive=False, required=True):
        self.label = label
        self.positive = positive
        self.required = required

    def validate(self, lang):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED, lang) % tr(self.label, lang)
        try:
            if int(self.value) > 0:
                is_positive = True
            failed_to_parse = False
        except:
            failed_to_parse = True
        if failed_to_parse or (self.positive and not is_positive):
            if self.positive:
                return tr("%s must be a positive integer.", lang) % tr(self.label, lang)
            else:
                return tr("%s must be an integer.", lang) % tr(self.label, lang)


class SubmitButton(Element):
    type = f"submit-button"

    def __init__(self, label):
        self.label = label


class Form:
    # Reserved field names
    # request, title, elements, is_valid, error
    def __init__(self, request, action=None, initial_values=None):
        lang = request.path[1:3]
        self.form_id = random_128_bit_string()
        self.request = request
        self.title = tr(self.__class__.__title__, lang)
        self.action = action
        self.elements = []
        self.is_valid = bool(request.POST)
        for name, element in self.get_elements():
            element = copy(element)
            if isinstance(element, Field):
                if isinstance(element, FileField):
                    self.enctype = f"multipart/form-data"
                element.set_name(name)
                if request.POST:
                    if isinstance(element, FileField):
                        value = request.FILES.get(name)
                    else:
                        value = request.POST.get(name)
                    element.set_value(value)
                    element.set_error(element.validate(lang))
                    self.__dict__[name] = value
                    if element.error:
                        self.is_valid = False
                elif initial_values:
                    value = initial_values.get(name)
                    element.set_value(value)
                    self.__dict__[name] = value
            element.translate(lang)
            self.elements.append(element)
        if request.POST:
            self.validate(lang)

    def get_elements(self):
        return [(key, self.__class__.__dict__[key]) for key in self.__class__.__dict__.keys() if not key.startswith(f"__") and key not in f"validate"]

    def validate(self, lang):
        return None

    def add_error(self, *args):
        if len(args) == 1:
            self.error = args[0]
        else:
            for element in self.elements:
                if element.name == args[0]:
                    element.error = args[1]
                    break
        self.is_valid = False

    def render(self):
        return mark_safe(loader.render_to_string(f"form.html", {f"form": self}, self.request))
