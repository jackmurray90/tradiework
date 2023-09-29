from django.core.management.base import BaseCommand
from beatmatcher.translations import tr
import subprocess


class Command(BaseCommand):
    help = "Checks the translations"

    def handle(self, *args, **options):
        trs = subprocess.check_output(
            ["grep", "-hor", "tr\.[a-zA-Z0-9]*", "beatmatcher/templates"]
        )
        trs = [tr.split(".")[1] for tr in trs.decode("utf-8").split("\n") if tr]
        trs = set(trs)
        for lang in tr:
            missing = False
            for string in trs:
                if string not in tr[lang]:
                    print(lang, "is missing", string)
                    missing = True
            if not missing:
                print(lang, "has all translations")
