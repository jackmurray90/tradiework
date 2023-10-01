strings = []
translations = {
    "en": {},
    "de": {},
}


def tr(string, lang):
    return translations.get(lang, {}).get(string, string)


def register(string):
    strings.append(string)
    return string
