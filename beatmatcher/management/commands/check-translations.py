from django.core.management.base import BaseCommand
from beatmatcher.translations import tr

class Command(BaseCommand):
    help = "Checks the translations"

    def handle(self, *args, **options):
        max_length = 0
        max_lang = 'en'
        for lang in tr:
            if len(tr[lang]) > max_length:
                max_length = len(tr[lang])
                max_lang = lang
        for lang in tr:
            print("Count for", lang, "is", len(tr[lang]))
            if len(tr[lang]) < max_length:
                for string in tr[max_lang]:
                    if string not in tr[lang]:
                        print("    Missing:", string)
