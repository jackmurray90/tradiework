from django.utils.safestring import mark_safe
from django.template import loader
from app.translation import tr
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
    type = "text"
    MAXIMUM_CHARACTERS = "%s can be a maximum of %s characters."

    def __init__(self, label, model_field=None, required=True):
        self.label = label
        self.max_length = model_field.field.max_length if model_field else None
        self.required = required

    def validate(self, lang):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED, lang) % tr(self.label, lang)
        if self.max_length is not None and len(self.value) > self.max_length:
            return tr(self.MAXIMUM_CHARACTERS, lang) % (tr(self.label, lang), self.max_length)


class PasswordField(Field):
    type = "password"

    def __init__(self, label, required=True):
        self.label = label
        self.required = required

    def validate(self, lang):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED, lang) % tr(self.label, lang)

    def get_translation_strings(self):
        return [self.IS_REQUIRED, self.label]


class SubmitButton(Element):
    type = "submit-button"

    def __init__(self, label):
        self.label = label

    def get_translation_strings(self):
        return [self.label]


class Form:
    # Reserved field names
    # request, title, elements, is_valid, error
    def __init__(self, request):
        lang = request.path[1:3]
        self.request = request
        self.title = tr(self.__class__.__title__, lang)
        self.elements = []
        self.is_valid = bool(request.POST)
        for name, element in self.get_elements():
            element = copy(element)
            if isinstance(element, Field):
                element.set_name(name)
                if request.POST:
                    value = request.POST.get(name, None)
                    element.set_value(value)
                    element.set_error(element.validate(lang))
                    self.__dict__[name] = value
                    if element.error:
                        self.is_valid = False
            element.translate(lang)
            self.elements.append(element)
        if request.POST:
            self.validate(lang)

    def get_elements(self):
        return [
            (key, self.__class__.__dict__[key])
            for key in self.__class__.__dict__.keys()
            if not key.startswith("__") and key not in "validate"
        ]

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
        return mark_safe(loader.render_to_string("form.html", {"form": self}, self.request))
