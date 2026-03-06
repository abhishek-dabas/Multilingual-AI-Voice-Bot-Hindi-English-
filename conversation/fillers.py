import random

FILLERS = {
    "en": ["Hmm...", "Let me check..."],
    "hi": ["Haan...", "Ek second..."]
}

DEFAULT_LANG = "en"

def maybe_add_filler(text, lang, thinking=False):
    """
    Adds a filler ONLY when thinking.
    Falls back safely if language is unknown.
    """

    if not thinking or not text:
        return text

    # Fallback if ASR gives unexpected language
    if lang not in FILLERS:
        lang = DEFAULT_LANG

    return random.choice(FILLERS[lang]) + " " + text
