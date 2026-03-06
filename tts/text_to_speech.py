from gtts import gTTS
import uuid
import os

def synthesize_speech(text, lang):
    """
    Converts text to speech using gTTS.
    Returns path to generated audio file.
    """

    # Map language codes
    tts_lang = "hi" if lang == "hi" else "en"

    os.makedirs("tts_output", exist_ok=True)

    filename = f"tts_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join("tts_output",filename)

    tts = gTTS(text=text, lang=tts_lang, slow=False)
    tts.save(filepath)

    return filepath
