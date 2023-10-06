from django.utils.safestring import mark_safe
from django.template import loader
from app.translation import tr as app_tr
from app.util import random_128_bit_string
from copy import copy


class Element:
    # Translate all non-error strings required to be translated for this
    # element.
    def translate(self, tr):
        self.label = tr(self.label)


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

    def validate(self, tr):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED) % tr(self.label)
        if self.max_length is not None and len(self.value) > self.max_length:
            return tr("%s can be a maximum of %s characters.") % (tr(self.label), self.max_length)


class PasswordField(Field):
    type = f"password"

    def __init__(self, label, required=True):
        self.label = label
        self.required = required

    def validate(self, tr):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED) % tr(self.label)


class TextField(Field):
    type = f"textarea"

    def __init__(self, label, required=True):
        self.label = label
        self.required = required

    def validate(self, tr):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED) % tr(self.label)


class FileField(Field):
    type = f"file"

    def __init__(self, label, button_text, information_text=None, max_size=None, required=True):
        self.label = label
        self.button_text = button_text
        self.information_text = information_text
        self.max_size = max_size
        self.required = required

    def translate(self, tr):
        self.label = tr(self.label)
        self.button_text = tr(self.button_text)
        if self.information_text:
            self.information_text = tr(self.information_text)

    def max_size_readable(self):
        if self.max_size < 1024:
            return f"{self.max_size} bytes"
        if self.max_size < 1024 * 1024:
            return f"{self.max_size/1024} KB"
        if self.max_size < 1024 * 1024 * 1024:
            return f"{self.max_size/(1024*1024)} MB"
        return f"{self.max_size/(1024*1024*1024)} GB"

    def validate(self, tr):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED) % tr(self.label)
        if self.max_size and self.value and self.value.size > self.max_size:
            return tr("%s is too large. Maximum file size is %s") % (tr(self.label), self.max_size_readable())


class IntegerField(Field):
    type = f"text"

    def __init__(self, label, positive=False, required=True):
        self.label = label
        self.positive = positive
        self.required = required

    def validate(self, tr):
        if self.required and not self.value:
            return tr(self.IS_REQUIRED) % tr(self.label)
        try:
            if int(self.value) > 0:
                is_positive = True
            failed_to_parse = False
        except:
            failed_to_parse = True
        if failed_to_parse or (self.positive and not is_positive):
            if self.positive:
                return tr("%s must be a positive integer.") % tr(self.label)
            else:
                return tr("%s must be an integer.") % tr(self.label)


class HiddenField(Field):
    type = f"hidden"

    def __init__(self, model_field=None):
        self.choices = None
        if model_field and model_field.field.choices is not None:
            self.choices = set([x for x, _ in model_field.field.choices])

    def validate(self, tr):
        if self.choices is not None and self.value not in self.choices:
            # Does not need translation as field is hidden.
            return f"Invalid"

    def translate(self, tr):
        pass


class SelectField(Field):
    type = f"select"

    def __init__(self, label, model_field, required=True):
        self.label = label
        self.choices = [(f"", "Please select an option")] + model_field.field.choices
        self.required = required

    def validate(self, tr):
        if self.value not in set([x for x, _ in self.choices]):
            return tr("Invalid selection")
        if not self.value and self.required:
            return tr("Must selection an option")

    def translate(self, tr):
        self.label = tr(self.label)
        self.choices = [(value, tr(label)) for value, label in self.choices]


class SubmitButton(Element):
    type = f"submit-button"

    def __init__(self, label):
        self.label = label


class Form:
    # Reserved field names
    # request, title, elements, is_valid, error
    def __init__(self, request, action=None, initial_values=None, ignore_post=False):
        tr = lambda s: app_tr(s, request.session[f"language"])
        self.form_id = random_128_bit_string()
        self.request = request
        self.title = tr(self.__class__.__title__) if hasattr(self.__class__, f"__title__") else None
        self.action = action
        self.elements = []
        self.is_valid = bool(request.POST)
        for name, element in self.get_elements():
            element = copy(element)
            if isinstance(element, Field):
                if isinstance(element, FileField):
                    self.enctype = f"multipart/form-data"
                element.set_name(name)
                if request.POST and not ignore_post:
                    if isinstance(element, FileField):
                        value = request.FILES.get(name)
                    else:
                        value = request.POST.get(name)
                    element.set_value(value)
                    element.set_error(element.validate(tr))
                    self.__dict__[name] = value
                    if element.error:
                        self.is_valid = False
                elif initial_values:
                    value = initial_values.get(name)
                    element.set_value(value)
                    self.__dict__[name] = value
            element.translate(tr)
            self.elements.append(element)
        if request.POST and not ignore_post:
            self.validate(tr)

    def get_elements(self):
        return [(key, self.__class__.__dict__[key]) for key in self.__class__.__dict__.keys() if not key.startswith(f"__") and key not in f"validate"]

    def validate(self, tr):
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
