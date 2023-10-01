from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from app.translation import translations
from app.models import Language, String
from google.cloud import translate
import re

languages = [
    ("en", "English"),
    ("de", "Deutsch"),
]


def translate_text(text: str, target_language_code: str) -> translate.Translation:
    client = translate.TranslationServiceClient()
    response = client.translate_text(
        parent=f"projects/{settings.GOOGLE_CLOUD_PROJECT_ID}",
        contents=[text],
        target_language_code=target_language_code,
    )
    return response.translations[0].translated_text


class Command(BaseCommand):
    help = "Checks the translations"

    def handle(self, *args, **options):
        for code, name in languages:
            if not Language.objects.filter(code=code).first():
                Language.objects.create(code=code, name=name)

        all_strings = set()
        new_strings = set()
        error = False

        print("\nChecking new for strings in the code:\n")
        for path in list(Path("app/views").rglob("*.py")) + [Path("app/forms.py")]:
            if path.is_file():
                with open(path, "r") as f:
                    text = f.read()
                    for string in re.findall('."[^"]*"', text):
                        if string.endswith('\\"'):
                            print("Error: Unsupported string with backslash detected in", path)
                            error = True
                        if not string.startswith("f"):
                            string = string[2:-1]
                            all_strings.add(string)
                            if not String.objects.filter(language__code="en", english=string).first():
                                print(path, string)
                                new_strings.add(string)

        print("\nChecking for new strings in the templates:\n")
        for path in Path("app/templates").rglob("*"):
            if path.is_file():
                with open(path, "r") as f:
                    text = f.read()
                    for string in re.findall('(."[^"]*")\\|tr:lang', text):
                        if string.startswith("\\"):
                            print("Error: Unsupported string with backslash detected in", path)
                            error = True
                        string = string[2:-1]
                        all_strings.add(string)
                        if not String.objects.filter(language__code="en", english=string).first():
                            print(path, string)
                            new_strings.add(string)

        if new_strings:
            print('\nNew strings detected. Please check they look okay. If they are correct, enter "yes"')
            if input() != "yes":
                exit()

        for string in String.objects.all():
            string.in_use = string.english in all_strings
            string.save()

        if settings.GOOGLE_CLOUD_PROJECT_ID:
            print("\nAutomatically translating missing strings\n")
        for string in all_strings:
            for language in Language.objects.all():
                if not String.objects.filter(language=language, english=string).first():
                    if language.code == "en":
                        String.objects.create(language=language, english=string, translation=string, in_use=True)
                    elif settings.GOOGLE_CLOUD_PROJECT_ID:
                        translation = translate_text(string, language.code)
                        String.objects.create(language=language, english=string, translation=translation, in_use=True)
                        print(string, "-- translated to", language.name, "is --", translation)
        print("\nVisit http://localhost:8000/en/admin/language as a superuser to generate translation.py\n")

        print("\nChecking for untranslated strings in the templates:\n")
        for path in Path("app/templates").rglob("*"):
            if path.is_file():
                with open(path, "r") as f:
                    text = f.read()
                    text = text.replace("\n", " ")
                    text = re.sub("{{.*?}}", " ", text)
                    text = re.sub("{%.*?%}", " ", text)
                    text = re.sub("<style>.*?</style>", " ", text)
                    text = re.sub("<script>.*?</script>", " ", text)
                    text = re.sub("<.*?>", " ", text)
                    if re.search("\S", text):
                        print(path)
