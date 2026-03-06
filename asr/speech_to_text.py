"""
speech_to_text.py
=================

This module is responsible for converting raw audio into text
using OpenAI Whisper.

Responsibilities:
- Accept raw audio (numpy array)
- Run multilingual ASR (Hindi + English + code-mix)
- Return transcribed text and detected language

Why OpenAI Whisper:
- Excellent Hinglish support
- Stable on Windows
- No native compilation issues
- Easy to explain and debug
"""

import numpy as np
import whisper

# --------------------------------------------------
# Load Whisper model ONCE at startup
# --------------------------------------------------
# 'small' is a good balance between accuracy and speed
# You can switch to 'base' if CPU is slow
model = whisper.load_model("small")


def transcribe(audio_np: np.ndarray):
    """
    Transcribes speech audio into text using Whisper.

    Args:
        audio_np (np.ndarray):
            1-D numpy array containing audio samples
            sampled at 16kHz.

    Returns:
        text (str):
            Transcribed text from speech.
        lang (str):
            Detected language code ('en', 'hi', etc.)
    """

    # ----------------------------------------------
    # Whisper expects float32 audio in range [-1, 1]
    # ----------------------------------------------
    if audio_np.dtype != np.float32:
        audio_np = audio_np.astype(np.float32)

    # ----------------------------------------------
    # Run Whisper transcription
    # ----------------------------------------------
    # language=None enables automatic language detection
    # fp16=False is REQUIRED on CPU (Windows-safe)
    result = model.transcribe(
        audio_np,
        #language=None,
        task="transcribe",
        fp16=False,
        temperature=0.0
    )

    # ----------------------------------------------
    # Extract transcription text
    # ----------------------------------------------
    text = result.get("text", "").strip()

    # ----------------------------------------------
    # Extract detected language
    # ----------------------------------------------
    lang = result.get("language", "en")

    return text, lang
