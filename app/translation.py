translations = {
    "en": {},
    "de": {},
}


def tr(string, lang):
    return translations.get(lang, {}).get(string, string)
