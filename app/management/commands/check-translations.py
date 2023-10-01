from django.core.management.base import BaseCommand
from app.translation import translations
from pathlib import Path
import re


class Command(BaseCommand):
    help = "Checks the translations"

    def handle(self, *args, **options):
        print("\nChecking for strings in the code:\n")
        for path in list(Path("app/views").rglob("*.py")) + [Path("app/forms.py")]:
            with open(path, "r") as f:
                text = f.read()
                for string in re.findall('."[^"]*"', text):
                    if string.endswith('\\"'):
                        print("Warning: String with backslack detected in", path)
                    if not string.startswith("f"):
                        print(path, string[2:-1])

        print("\nChecking for strings in the templates:\n")
        for path in Path("app/templates").rglob("*"):
            if path.is_file():
                with open(path, "r") as f:
                    text = f.read()
                    for string in re.findall('"([^"]*)"\\|tr:lang', text):
                        print(path, string)

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
